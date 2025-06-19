#!/usr/bin/env python3
"""
Advanced Side-Channel Data Collection System
Automatically collects advanced multi-channel traces for training sophisticated models
"""

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
import sqlite3
import numpy as np
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import shutil

# Import advanced data converter
from advanced_data_converter import AdvancedDataConverter

WEBSITES = [
    "https://cse.buet.ac.bd/moodle/",
    "https://google.com", 
    "https://prothomalo.com",
]

TRACES_PER_SITE = 50
FINGERPRINTING_URL = "http://localhost:5000"  # Use same server as collect.py
ADVANCED_OUTPUT_PATH = "Datasets/advanced_dataset.json"
ADVANCED_DB_PATH = "advanced_webfingerprint.db"

# Default configuration options
HEADLESS_MODE = True
BACKGROUND_MODE = True

class AdvancedDatabase:
    """Simple database handler for advanced traces"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the advanced traces database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create advanced traces table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS advanced_traces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            website TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            trace_data TEXT NOT NULL,
            feature_vector TEXT NOT NULL,
            success BOOLEAN DEFAULT 1
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def count_traces(self, website: str) -> int:
        """Count traces for a specific website"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM advanced_traces WHERE website = ?', (website,))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def save_trace(self, website: str, trace_data: dict, feature_vector: np.ndarray) -> bool:
        """Save an advanced trace to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO advanced_traces (website, trace_data, feature_vector)
            VALUES (?, ?, ?)
            ''', (
                website,
                json.dumps(trace_data),
                json.dumps(feature_vector.tolist())
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Database error: {e}")
            return False
    
    def export_to_json(self, output_path: str) -> int:
        """Export all traces to JSON format"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT website, feature_vector FROM advanced_traces')
        
        dataset = []
        for row in cursor.fetchall():
            website, feature_vector_json = row
            feature_vector = json.loads(feature_vector_json)
            
            dataset.append({
                "website": website,
                "trace_data": feature_vector
            })
        
        conn.close()
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(dataset, f, indent=2)
        
        return len(dataset)

def setup_webdriver():
    """Set up the Selenium WebDriver with Chrome options (same as collect.py)."""
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
        temp_dir = tempfile.mkdtemp(prefix="chrome_advanced_")
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

def is_server_running(host='127.0.0.1', port=5000):
    """Check if the Flask server is running."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

def collect_advanced_trace(driver, website: str, wait) -> dict:
    """Collect advanced trace for a website - CORRECT SEQUENCE: (1) Click collect FIRST, (2) Then navigate to website"""
    try:
        # 1. Go to fingerprinting site
        driver.get(FINGERPRINTING_URL)
        
        # 2. Wait for Alpine.js app to be ready
        print("Debug: Waiting for Alpine.js app to initialize...")
        max_init_wait = 10
        for _ in range(max_init_wait):
            app_ready = driver.execute_script("""
                return typeof window.app !== 'undefined' && 
                       window.app && 
                       typeof window.app.collectAdvancedTraceData === 'function';
            """)
            if app_ready:
                print("Debug: Alpine.js app is ready!")
                break
            time.sleep(1)
        else:
            print("Debug: Warning - Alpine.js app may not be ready")
        
        # 3. FIRST: Click the "Collect Advanced Trace" button to START collection
        trace_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Collect Advanced Trace')]")))
        print("Debug: Clicking 'Collect Advanced Trace' button FIRST...")
        trace_button.click()
        
        # Small delay to let collection start
        time.sleep(2)
        
        # 4. THEN: Open target site in new tab (this triggers the side-channel activity)
        print(f"Debug: Now navigating to {website} to trigger collection...")
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        
        try:
            # Set longer timeout for slow websites
            driver.set_page_load_timeout(30)
            driver.get(website)
            print(" loaded", end="")
            
            # Wait for initial page load
            time.sleep(2)
            
            # Interact with the page to generate more browser activity
            # Scroll down multiple times to trigger more cache activity
            for _ in range(3):
                driver.execute_script("window.scrollBy(0, window.innerHeight);")
                time.sleep(0.5)
            print(" scrolled", end="")
            
            # Scroll back up
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.5)
            
            # Try to click some elements if they exist (safe clicking)
            try:
                driver.execute_script("""
                    const links = document.querySelectorAll('a');
                    if (links.length > 0) {
                        links[0].focus();
                    }
                """)
            except:
                pass
            
            # Wait a bit more for the side-channel to capture activity
            time.sleep(2)
            print(" interacted", end="")
            
        except Exception as e:
            print(f" load_error:{str(e)[:20]}", end="")
        finally:
            # 5. Wait for page to load completely (this is when the collection happens)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        
        # 5. Wait for advanced trace collection to complete
        print(f"Debug: Waiting for collection to complete...")
        max_wait = 60  # 60 seconds max
        for _ in range(max_wait):
            try:
                # Check if collection is complete by monitoring the status
                app_exists = driver.execute_script("return typeof window.app !== 'undefined'")
                if not app_exists:
                    print(f"Debug: window.app doesn't exist yet")
                    time.sleep(1)
                    continue
                    
                is_collecting = driver.execute_script("return window.app ? window.app.isCollecting : false")
                status = driver.execute_script("return window.app ? window.app.status : 'No status'")
                print(f"Debug: isCollecting={is_collecting}, status='{status}'")
                
                if not is_collecting:
                    print(f"Debug: Collection appears complete")
                    break
                time.sleep(1)
            except Exception as e:
                print(f"Debug: Exception checking status: {e}")
                time.sleep(1)
        
        # 6. Get the latest trace data - try multiple methods
        trace_data = None
        
        # Method 1: Check Alpine.js app data
        trace_data = driver.execute_script("""
            if (window.app && window.app.traceData && window.app.traceData.length > 0) {
                const latestTrace = window.app.traceData[window.app.traceData.length - 1];
                console.log('Found trace in app.traceData:', latestTrace);
                return latestTrace;
            }
            return null;
        """)
        
        # Method 2: If that failed, try to get from backend API
        if not trace_data:
            try:
                trace_data = driver.execute_script("""
                    return fetch('/download_traces')
                        .then(response => response.json())
                        .then(data => {
                            console.log('Backend traces:', data);
                            return data && data.length > 0 ? data[data.length - 1] : null;
                        })
                        .catch(err => {
                            console.error('Error fetching traces:', err);
                            return null;
                        });
                """)
                # Wait for the promise to resolve
                time.sleep(2)
            except Exception:
                pass
        
        # Method 3: Try to get directly from any global variables
        if not trace_data:
            trace_data = driver.execute_script("""
                // Look for any trace data in global scope
                if (typeof advancedTraceData !== 'undefined') {
                    console.log('Found advancedTraceData:', advancedTraceData);
                    return advancedTraceData;
                }
                if (typeof lastTraceData !== 'undefined') {
                    console.log('Found lastTraceData:', lastTraceData);
                    return lastTraceData;
                }
                console.log('No trace data found in any location');
                return null;
            """)
        
        print(f"Debug: Got trace data: {bool(trace_data)}")
        if trace_data:
            print(f"Debug: Trace keys: {list(trace_data.keys()) if isinstance(trace_data, dict) else 'Not a dict'}")
            if isinstance(trace_data, dict):
                print(f"Debug: Sample keys from trace: {list(trace_data.keys())[:5]}")
        
        if trace_data:
            trace_data['target_website'] = website
            trace_data['collection_timestamp'] = datetime.now().isoformat()
            return trace_data
        else:
            return {}
            
    except Exception as e:
        print(f"Error collecting trace for {website}: {e}")
        return {}

def main():
    global HEADLESS_MODE, TRACES_PER_SITE, WEBSITES, FINGERPRINTING_URL, ADVANCED_OUTPUT_PATH, ADVANCED_DB_PATH

    parser = argparse.ArgumentParser(description='Advanced Side-Channel Data Collection System')
    parser.add_argument('--traces', type=int, default=TRACES_PER_SITE, help=f'Traces per site (default: {TRACES_PER_SITE})')
    parser.add_argument('--headless', action='store_true', default=HEADLESS_MODE, help='Run in headless mode')
    parser.add_argument('--show-browser', action='store_true', help='Show browser (disable headless)')
    parser.add_argument('--test', action='store_true', help='Test mode - just show stats, no collection')
    parser.add_argument('--websites', type=str, help='Comma-separated list of websites to collect from (default: all)')
    parser.add_argument('--site-index', type=int, choices=range(len(WEBSITES)), help='Collect only for this site index (0=moodle, 1=google, 2=prothomalo)')
    
    args = parser.parse_args()
    
    # Update globals based on args
    TRACES_PER_SITE = args.traces
    if args.show_browser:
        HEADLESS_MODE = False
    elif args.headless:
        HEADLESS_MODE = True
    
    # Filter websites if specified
    target_websites = WEBSITES.copy()
    if args.websites:
        specified_websites = [w.strip() for w in args.websites.split(',')]
        target_websites = [w for w in WEBSITES if any(spec in w for spec in specified_websites)]
        if not target_websites:
            print(f"❌ No matching websites found for: {specified_websites}")
            print(f"Available websites: {WEBSITES}")
            return
    elif args.site_index is not None:
        target_websites = [WEBSITES[args.site_index]]

    print("🚀 Advanced Side-Channel Data Collection System")
    print("=" * 50)
    
    # Simple test mode first
    print("🧪 Running in simple test mode")
    print(f"📊 Will collect {TRACES_PER_SITE} traces per site")
    print(f"🌐 Target websites: {len(target_websites)}")
    if len(target_websites) < len(WEBSITES):
        print(f"🎯 Filtering to: {target_websites}")
    
    # Initialize database
    print("🧠 Initializing advanced database...")
    advanced_db = AdvancedDatabase(ADVANCED_DB_PATH)
    print(f"Database initialized at: {os.path.abspath(ADVANCED_DB_PATH)}")
    
    # Show current stats
    print("\n📊 Current advanced trace counts:")
    for site in target_websites:
        count = advanced_db.count_traces(site)
        print(f"  {site}: {count}/{TRACES_PER_SITE}")
    
    total_needed = sum(max(0, TRACES_PER_SITE - advanced_db.count_traces(w)) for w in target_websites)
    print(f"\n🎯 Need to collect {total_needed} more advanced traces")
    
    if total_needed == 0:
        print("\n✅ All targeted traces already collected!")
        # Export dataset
        exported_count = advanced_db.export_to_json(ADVANCED_OUTPUT_PATH)
        print(f"✅ Advanced dataset exported to {ADVANCED_OUTPUT_PATH} ({exported_count} traces)")
        return
    
    if args.test:
        print("\n🧪 Test mode - skipping collection")
        return
    
    # Run collection
    run_collection(advanced_db, total_needed, target_websites)

def run_collection(advanced_db, total_needed, target_websites):
    """Run the actual trace collection process"""
    print(f"\n🚀 Starting collection of {total_needed} advanced traces...")
    
    # Initialize data converter
    converter = AdvancedDataConverter()
    
    # Setup Chrome driver
    print("🌐 Setting up Chrome driver...")
    driver = setup_webdriver()
    wait = WebDriverWait(driver, 10)
    
    try:
        # Check if server is running
        if not is_server_running():
            print("❌ Flask server not running at localhost:5000")
            print("   Please start it with: python app.py")
            return
        
        print("✅ Flask server is running")
        
        # Collect traces for each website
        collect_traces_for_websites(driver, advanced_db, converter, wait, target_websites)
        
    finally:
        driver.quit()
        print("🔚 Chrome driver closed")

def collect_traces_for_websites(driver, advanced_db, converter, wait, target_websites):
    """Collect traces for specified websites"""
    total_collected = 0
    for website in target_websites:
        current_count = advanced_db.count_traces(website)
        needed = TRACES_PER_SITE - current_count
        
        if needed <= 0:
            continue
            
        print(f"\n🎯 Collecting {needed} traces for {website}...")
        
        for i in range(needed):
            try:
                print(f"  📊 Trace {i+1}/{needed} for {website}...", end=" ")
                
                # Collect trace
                trace_data = collect_advanced_trace(driver, website, wait)
                
                if trace_data and ('timings' in trace_data or 'attacks' in trace_data):
                    # Convert to feature vector
                    feature_vector = converter.convert_advanced_trace(trace_data)
                    
                    # Save to database
                    if advanced_db.save_trace(website, trace_data, feature_vector):
                        print("✅")
                        total_collected += 1
                    else:
                        print("❌ (save failed)")
                else:
                    print("❌ (no data)")
                    
                # Small delay between traces
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ (error: {e})")
                continue
    
    print(f"\n🎉 Collection complete! Collected {total_collected} new traces")
    
    # Export to JSON
    exported_count = advanced_db.export_to_json(ADVANCED_OUTPUT_PATH)
    print(f"✅ Advanced dataset exported to {ADVANCED_OUTPUT_PATH} ({exported_count} total traces)")

if __name__ == "__main__":
    main()
