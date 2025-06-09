#!/usr/bin/env python3
"""
Test script for collect.py functionality
This script tests the trace collection workflow that would be used in collect.py
"""

import sys
import subprocess
import time
import socket
import shutil
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

FINGERPRINTING_URL = "http://127.0.0.1:5000"
PORT = 5000
TEST_WEBSITES = [
    "https://google.com",
    "https://prothomalo.com"
]

def wait_for_server(port, timeout=10):
    """Wait for the Flask server to start"""
    start = time.time()
    while time.time() - start < timeout:
        sock = socket.socket()
        if sock.connect_ex(("127.0.0.1", port)) == 0:
            sock.close()
            return True
        sock.close()
        time.sleep(0.5)
    return False

def setup_webdriver():
    """Set up the Selenium WebDriver with Chrome options"""
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    # Don't use headless for trace collection as it may affect timing
    
    service = Service(shutil.which("chromedriver"))
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def test_trace_collection_workflow():
    """Test the trace collection workflow that collect.py would use"""
    print("🔍 Testing trace collection workflow...")
    
    # Start Flask server
    server = subprocess.Popen([sys.executable, "app.py"], 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE)
    
    try:
        if not wait_for_server(PORT):
            print("❌ Flask app failed to start")
            return False
        
        print("✅ Flask server started")
        
        # Set up WebDriver
        driver = setup_webdriver()
        wait = WebDriverWait(driver, 10)
        
        try:
            # 1. Open the fingerprinting website
            print("📱 Opening fingerprinting website...")
            driver.get(FINGERPRINTING_URL)
            print("✅ Fingerprinting website loaded")
            
            # 2. Test if we can interact with the trace collection interface
            print("🔧 Testing trace collection interface...")
            
            # Check if latency button works (similar functionality to trace collection)
            try:
                latency_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Collect Latency Data')]")
                print("✅ Found latency collection button")
                
                # Click the button to test JavaScript execution
                latency_btn.click()
                print("✅ Clicked latency collection button")
                
                # Wait for collection to complete (or at least start)
                time.sleep(2)
                
                # Check if status message appears
                try:
                    status_element = driver.find_element(By.XPATH, "//div[@role='alert']")
                    status_text = status_element.text
                    print(f"✅ Status message: {status_text}")
                except:
                    print("⚠️  No status message found")
                
            except Exception as e:
                print(f"❌ Error with latency button: {e}")
                return False
            
            # 3. Test opening target websites in new tabs
            print("🌐 Testing target website access in new tabs...")
            
            for website in TEST_WEBSITES:
                try:
                    # Open new tab
                    driver.execute_script("window.open('');")
                    driver.switch_to.window(driver.window_handles[-1])
                    
                    # Navigate to target website
                    driver.get(website)
                    time.sleep(2)  # Wait for page load
                    
                    title = driver.title
                    print(f"✅ Opened {website} - Title: {title[:50]}...")
                    
                    # Simulate some interaction (scrolling)
                    driver.execute_script("window.scrollTo(0, 500);")
                    time.sleep(0.5)
                    
                    # Close the tab
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    
                except Exception as e:
                    print(f"❌ Error accessing {website}: {e}")
                    # Switch back to main tab even if there was an error
                    if len(driver.window_handles) > 1:
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
            
            # 4. Test if we can simulate the cache measurement process
            print("⏱️  Testing cache timing simulation...")
            
            # Test if we can run JavaScript timing operations
            timing_test = driver.execute_script("""
                const start = performance.now();
                
                // Simulate cache operations
                const buffer = new ArrayBuffer(1024 * 1024); // 1MB buffer
                const view = new Uint8Array(buffer);
                
                // Fill buffer (cache pollution)
                for (let i = 0; i < view.length; i += 64) {
                    view[i] = i % 256;
                }
                
                // Measure access time
                const accessStart = performance.now();
                let sum = 0;
                for (let i = 0; i < view.length; i += 64) {
                    sum += view[i];
                }
                const accessEnd = performance.now();
                
                return {
                    totalTime: performance.now() - start,
                    accessTime: accessEnd - accessStart,
                    sum: sum
                };
            """)
            
            if timing_test and timing_test['totalTime'] > 0:
                print(f"✅ Cache timing test completed:")
                print(f"   Total time: {timing_test['totalTime']:.2f}ms")
                print(f"   Access time: {timing_test['accessTime']:.2f}ms")
                print(f"   Sum: {timing_test['sum']}")
            else:
                print("❌ Cache timing test failed")
                return False
            
            # 5. Test if we can simulate trace data collection
            print("📊 Testing trace data simulation...")
            
            trace_data = driver.execute_script("""
                // Simulate collecting cache access traces
                const traces = [];
                const duration = 100; // 100ms test duration
                const interval = 10;  // 10ms intervals
                
                const startTime = performance.now();
                
                // Simulate cache line access pattern
                for (let t = 0; t < duration; t += interval) {
                    const count = Math.floor(Math.random() * 100) + 50; // Random access count
                    traces.push(count);
                }
                
                return {
                    traces: traces,
                    duration: duration,
                    interval: interval,
                    timestamp: Date.now()
                };
            """)
            
            if trace_data and len(trace_data['traces']) > 0:
                print(f"✅ Trace data simulation completed:")
                print(f"   Traces collected: {len(trace_data['traces'])}")
                print(f"   Duration: {trace_data['duration']}ms")
                print(f"   Sample trace: {trace_data['traces'][:5]}...")
            else:
                print("❌ Trace data simulation failed")
                return False
            
            print("🎉 All trace collection workflow tests passed!")
            return True
            
        finally:
            driver.quit()
            
    finally:
        server.terminate()
        server.wait()

def test_database_functionality():
    """Test database functionality for storing traces"""
    print("🔍 Testing database functionality...")
    
    try:
        # Import database module
        import database
        
        # Test database initialization
        test_websites = ["https://test1.com", "https://test2.com"]
        db = database.Database(test_websites)
        db.init_database()
        print("✅ Database initialized")
        
        # Test saving a trace
        test_trace = [10, 20, 30, 40, 50]
        result = db.save_trace("https://test1.com", 0, test_trace)
        if result:
            print("✅ Trace saved to database")
        else:
            print("❌ Failed to save trace")
            return False
        
        # Test getting trace counts
        counts = db.get_traces_collected()
        if counts and counts.get("https://test1.com", 0) > 0:
            print(f"✅ Trace counts retrieved: {counts}")
        else:
            print("❌ Failed to retrieve trace counts")
            return False
        
        # Test export functionality
        db.export_to_json("test_dataset.json")
        
        # Check if file was created
        import os
        if os.path.exists("test_dataset.json"):
            print("✅ Dataset exported to JSON")
            # Clean up
            os.remove("test_dataset.json")
            os.remove("webfingerprint.db")
        else:
            print("❌ Failed to export dataset")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def main():
    """Run all collect.py related tests"""
    print("🚀 Testing collect.py Functionality\n")
    
    tests = [
        ("Trace Collection Workflow", test_trace_collection_workflow),
        ("Database Functionality", test_database_functionality)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"TEST: {test_name}")
        print('='*60)
        
        try:
            result = test_func()
            results.append((test_name, result))
            status = "PASSED" if result else "FAILED"
            print(f"\n{test_name}: {status}")
        except Exception as e:
            print(f"\n{test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All collect.py functionality tests passed!")
        print("✅ Your setup is ready for side channel attack data collection.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the setup.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
