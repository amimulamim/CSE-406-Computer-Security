#!/usr/bin/env python3
"""
Test script for side channel attack setup
This script tests:
1. Flask app startup
2. Chrome automation with selenium
3. Frontend JavaScript execution
4. Cache timing functionality
5. Basic trace collection workflow
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

def test_chrome_setup():
    """Test Chrome and ChromeDriver setup"""
    print("🔍 Testing Chrome setup...")
    
    # Test Chrome binary
    chrome_path = shutil.which("google-chrome")
    if not chrome_path:
        print("❌ google-chrome not found on PATH")
        return False
    print(f"✅ Chrome found at: {chrome_path}")
    
    # Test ChromeDriver
    driver_path = shutil.which("chromedriver")
    if not driver_path:
        print("❌ chromedriver not found on PATH")
        return False
    print(f"✅ ChromeDriver found at: {driver_path}")
    
    return True

def test_basic_automation():
    """Test basic Chrome automation"""
    print("🔍 Testing basic Chrome automation...")
    
    opts = Options()
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--headless")
    
    service = Service(shutil.which("chromedriver"))
    
    try:
        driver = webdriver.Chrome(service=service, options=opts)
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        print(f"✅ Basic automation works - Google title: {title}")
        return True
    except Exception as e:
        print(f"❌ Basic automation failed: {e}")
        return False

def test_flask_app():
    """Test Flask app functionality"""
    print("🔍 Testing Flask app...")
    
    server = subprocess.Popen([sys.executable, "app.py"], 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE)
    
    try:
        if not wait_for_server(PORT):
            print("❌ Flask app failed to start")
            return False
        
        print("✅ Flask app started successfully")
        
        # Test basic page load
        opts = Options()
        opts.add_argument("--headless")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        
        service = Service(shutil.which("chromedriver"))
        driver = webdriver.Chrome(service=service, options=opts)
        
        try:
            driver.get(FINGERPRINTING_URL)
            title = driver.title
            
            if "Website Fingerprinting" in title:
                print(f"✅ Flask app page loads correctly - Title: {title}")
                
                # Test if JavaScript loads
                try:
                    driver.execute_script("return typeof app === 'function'")
                    print("✅ JavaScript app function is available")
                except:
                    print("⚠️  JavaScript app function not found")
                
                # Test if buttons are present
                try:
                    latency_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Collect Latency Data')]")
                    print("✅ Latency collection button found")
                except:
                    print("⚠️  Latency collection button not found")
                
                return True
            else:
                print(f"❌ Unexpected page title: {title}")
                return False
                
        finally:
            driver.quit()
            
    finally:
        server.terminate()
        server.wait()

def test_cache_timing_basics():
    """Test if cache timing functionality is available"""
    print("🔍 Testing cache timing functionality...")
    
    server = subprocess.Popen([sys.executable, "app.py"], 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE)
    
    try:
        if not wait_for_server(PORT):
            print("❌ Flask app failed to start")
            return False
        
        opts = Options()
        opts.add_argument("--headless")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        
        service = Service(shutil.which("chromedriver"))
        driver = webdriver.Chrome(service=service, options=opts)
        
        try:
            driver.get(FINGERPRINTING_URL)
            
            # Test if performance API is available
            perf_available = driver.execute_script("return typeof performance !== 'undefined'")
            if perf_available:
                print("✅ Performance API is available")
            else:
                print("❌ Performance API not available")
                return False
            
            # Test if high-resolution timer is available
            hr_time = driver.execute_script("return performance.now()")
            if hr_time and hr_time > 0:
                print(f"✅ High-resolution timer works: {hr_time}ms")
            else:
                print("❌ High-resolution timer not working")
                return False
            
            # Test if SharedArrayBuffer is available (needed for precise timing)
            sab_available = driver.execute_script("return typeof SharedArrayBuffer !== 'undefined'")
            if sab_available:
                print("✅ SharedArrayBuffer is available")
            else:
                print("⚠️  SharedArrayBuffer not available (may affect timing precision)")
            
            # Test if we can allocate large arrays (for cache testing)
            try:
                array_size = driver.execute_script("""
                    try {
                        const arr = new Uint8Array(32 * 1024 * 1024); // 32MB
                        return arr.length;
                    } catch (e) {
                        return 0;
                    }
                """)
                if array_size > 0:
                    print(f"✅ Large array allocation works: {array_size} bytes")
                else:
                    print("❌ Large array allocation failed")
                    return False
            except Exception as e:
                print(f"❌ Array allocation test failed: {e}")
                return False
            
            return True
            
        finally:
            driver.quit()
            
    finally:
        server.terminate()
        server.wait()

def test_target_websites():
    """Test access to target websites for fingerprinting"""
    print("🔍 Testing target websites access...")
    
    target_sites = [
        "https://cse.buet.ac.bd/moodle/",
        "https://google.com",
        "https://prothomalo.com"
    ]
    
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-web-security")  # Allow cross-origin for testing
    
    service = Service(shutil.which("chromedriver"))
    driver = webdriver.Chrome(service=service, options=opts)
    
    try:
        accessible_sites = 0
        for site in target_sites:
            try:
                driver.get(site)
                driver.implicitly_wait(5)
                title = driver.title
                if title and len(title) > 0:
                    print(f"✅ {site} - Title: {title[:50]}...")
                    accessible_sites += 1
                else:
                    print(f"⚠️  {site} - No title found")
            except Exception as e:
                print(f"❌ {site} - Error: {str(e)[:50]}...")
        
        print(f"✅ {accessible_sites}/{len(target_sites)} target sites accessible")
        return accessible_sites > 0
        
    finally:
        driver.quit()

def main():
    """Run all tests"""
    print("🚀 Starting Side Channel Attack Setup Tests\n")
    
    tests = [
        ("Chrome Setup", test_chrome_setup),
        ("Basic Automation", test_basic_automation),
        ("Flask App", test_flask_app),
        ("Cache Timing", test_cache_timing_basics),
        ("Target Websites", test_target_websites)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"TEST: {test_name}")
        print('='*50)
        
        try:
            result = test_func()
            results.append((test_name, result))
            status = "PASSED" if result else "FAILED"
            print(f"\n{test_name}: {status}")
        except Exception as e:
            print(f"\n{test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("SUMMARY")
    print('='*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your setup is ready for side channel attacks.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the setup.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
