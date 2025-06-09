import time
import json
import os
import signal
import sys
import random
import traceback
import socket
import tempfile
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import shutil
import database
from database import Database

WEBSITES = [
    "https://cse.buet.ac.bd/moodle/",
    "https://google.com",
    "https://prothomalo.com",
]

TRACES_PER_SITE = 1000
FINGERPRINTING_URL = "http://localhost:5000" 
OUTPUT_PATH = "dataset.json"

# Default configuration options (can be overridden with command line args)
HEADLESS_MODE = True  # Set to False if you need to see the browser for debugging
BACKGROUND_MODE = True  # Minimize browser disruption

database.db = Database(WEBSITES)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Collect side channel attack traces')
    parser.add_argument('--visible', action='store_true', 
                       help='Run browser in visible mode (not headless)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode (visible browser + verbose output)')
    parser.add_argument('--traces', type=int, default=TRACES_PER_SITE,
                       help=f'Number of traces per site (default: {TRACES_PER_SITE})')
    return parser.parse_args()

def signal_handler(sig, frame):
    print("\nInterrupted. Saving dataset...")
    try:
        database.db.export_to_json(OUTPUT_PATH)
    except Exception as e:
        print(f"⚠️ Failed to export: {e}")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def is_server_running(host='127.0.0.1', port=5000):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

def setup_webdriver():
    """Set up the Selenium WebDriver with Chrome options."""
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    
    # Background/headless mode configuration
    if HEADLESS_MODE:
        chrome_options.add_argument("--headless")
        print("🎭 Running in headless mode (browser hidden)")
    
    if BACKGROUND_MODE:
        # Additional options to minimize system disruption
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-prompt-on-repost")
        chrome_options.add_argument("--disable-hang-monitor")
        chrome_options.add_argument("--disable-ipc-flooding-protection")
        
        # Set a separate user data directory to avoid interfering with your main browser
        temp_dir = tempfile.mkdtemp(prefix="chrome_sidechain_")
        chrome_options.add_argument(f"--user-data-dir={temp_dir}")
        print(f"🔒 Using separate Chrome profile: {temp_dir}")
    
    # Use system chromedriver instead of webdriver-manager
    driver_path = shutil.which("chromedriver")
    if not driver_path:
        print("❌ chromedriver not found on PATH")
        sys.exit(1)
    
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def retrieve_traces_from_backend(driver):
    """Retrieve traces from the backend API."""
    traces = driver.execute_script("""
        return fetch('/download_traces')
            .then(response => response.ok ? response.json() : [])
            .catch(() => []);
    """)
    
    count = len(traces) if traces else 0
    print(f"  - Retrieved {count} traces from backend API" if count else "  - No traces found in backend storage")
    return traces or []

def clear_trace_results(driver, wait):
    """Clear all results from the backend by pressing the button."""
    try:
        clear_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Clear Results')]")
        clear_button.click()

        wait.until(EC.text_to_be_present_in_element(
            (By.XPATH, "//div[@role='alert']"), "cleared"))
        print("🧹 Cleared backend results.")
    except Exception as e:
        print(f"⚠️ Could not clear backend results: {e}")

def is_collection_complete():
    current_counts = database.db.get_traces_collected()
    remaining = sum(max(0, TRACES_PER_SITE - current_counts.get(w, 0)) for w in WEBSITES)
    return remaining == 0

def collect_single_trace(driver, wait, website_url):
    """Collect a single trace for a website."""
    try:
        # 1. Go to fingerprinting site
        driver.get(FINGERPRINTING_URL)
        
        # Wait for and click the "Collect Trace" button
        trace_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Collect Trace')]")))
        trace_button.click()

        # 2. Open target site in new tab
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(website_url)
        time.sleep(2)

        # 3. Simulate user behavior
        for _ in range(5):
            y = random.randint(200, 1000)
            driver.execute_script(f"window.scrollTo(0, {y});")
            time.sleep(random.uniform(0.5, 1.0))

        # 4. Return to fingerprinting tab
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(12)  # Wait for trace to be collected

        # 5. Fetch trace
        traces = retrieve_traces_from_backend(driver)
        if not traces:
            print("❌ No trace collected.")
            return False
        trace = traces[-1]
        print(f"✅ Trace for {website_url} — {len(trace)} samples")

        # 6. Save to DB
        return database.db.save_trace(website_url, WEBSITES.index(website_url), trace)

    except Exception as e:
        print(f"❌ Error collecting trace for {website_url}: {e}")
        traceback.print_exc()
        return False

def collect_fingerprints(driver):
    wait = WebDriverWait(driver, 10)
    total_collected = 0

    while not is_collection_complete():
        for site in WEBSITES:
            count = database.db.get_traces_collected().get(site, 0)
            if count >= TRACES_PER_SITE:
                continue

            print(f"\n🌐 Collecting trace #{count + 1} for {site}")
            success = collect_single_trace(driver, wait, site)
            if success:
                total_collected += 1
            else:
                print("⚠️ Retrying trace collection after short delay...")
                time.sleep(2)

    print(f"\n✅ Finished collecting {total_collected} new traces.")
    return total_collected

def main():
    global HEADLESS_MODE, BACKGROUND_MODE, TRACES_PER_SITE
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Override configuration based on arguments
    if args.visible or args.debug:
        HEADLESS_MODE = False
        print("👁️  Running in visible mode (as requested)")
    
    if args.debug:
        BACKGROUND_MODE = False
        print("🐛 Debug mode enabled - browser will be more visible")
    
    TRACES_PER_SITE = args.traces
    
    if not is_server_running():
        print("❌ Flask server not running. Start it with: python3 app.py")
        return

    print("🧠 Initializing database...")
    database.db.init_database()
    
    # Show current progress
    current_counts = database.db.get_traces_collected()
    total_needed = len(WEBSITES) * TRACES_PER_SITE
    total_current = sum(current_counts.values())
    
    print(f"📊 Current progress: {total_current}/{total_needed} traces collected")
    for website, count in current_counts.items():
        print(f"  - {website}: {count}/{TRACES_PER_SITE}")
    
    if is_collection_complete():
        print("✅ Collection already complete!")
        return

    mode_str = "headless" if HEADLESS_MODE else "visible"
    background_str = " (background)" if BACKGROUND_MODE else ""
    print(f"🚀 Launching browser in {mode_str} mode{background_str}...")
    driver = setup_webdriver()

    try:
        print("⚙️ Navigating to fingerprinting page to clear old results...")
        driver.get(FINGERPRINTING_URL)
        wait = WebDriverWait(driver, 10)
        clear_trace_results(driver, wait)

        print("🧪 Starting fingerprint collection...")
        print("💡 You can now continue working - the browser is running in the background!")
        print("   Press Ctrl+C to stop collection and save progress.")
        
        collect_fingerprints(driver)

    except KeyboardInterrupt:
        print("\n❗ Interrupted by user.")
    except Exception as e:
        print(f"❌ Error during collection: {e}")
        traceback.print_exc()
    finally:
        print("🧹 Cleaning up browser...")
        driver.quit()
        print("💾 Exporting final dataset...")
        database.db.export_to_json(OUTPUT_PATH)
        print(f"✅ Dataset saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
