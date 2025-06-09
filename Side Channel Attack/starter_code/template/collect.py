import time
import json
import os
import signal
import sys
import random
import traceback
import socket
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
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

database.db = Database(WEBSITES)

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
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def retrieve_traces_from_backend(driver):
    return driver.execute_script("""
        return fetch('/download_traces')
            .then(r => r.ok ? r.json() : [])
            .catch(() => []);
    """)

def clear_trace_results(driver, wait):
    try:
        clear_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Clear Results')]")
        clear_button.click()
        wait.until(EC.text_to_be_present_in_element(
            (By.XPATH, "//div[@role='alert']"), "cleared"))
        print("🧹 Cleared backend results.")
    except:
        print("⚠️ Could not clear backend results.")

def is_collection_complete():
    current_counts = database.db.get_traces_collected()
    remaining = sum(max(0, TRACES_PER_SITE - current_counts.get(w, 0)) for w in WEBSITES)
    return remaining == 0

def collect_single_trace(driver, wait, website_url):
    try:
        # 1. Go to fingerprinting site
        driver.get(FINGERPRINTING_URL)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Collect Trace')]"))).click()

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
    if not is_server_running():
        print("❌ Flask server not running. Start it with: python3 app.py")
        return

    print("🧠 Initializing database...")
    database.db.init_database()

    print("🚀 Launching browser...")
    driver = setup_webdriver()

    try:
        print("⚙️ Navigating to fingerprinting page to clear old results...")
        driver.get(FINGERPRINTING_URL)
        wait = WebDriverWait(driver, 10)
        clear_trace_results(driver, wait)

        print("🧪 Starting fingerprint collection...")
        collect_fingerprints(driver)

    except KeyboardInterrupt:
        print("❗ Interrupted by user.")
    except Exception as e:
        print(f"❌ Error during collection: {e}")
    finally:
        driver.quit()
        print("💾 Exporting final dataset...")
        database.db.export_to_json(OUTPUT_PATH)

if __name__ == "__main__":
    main()
