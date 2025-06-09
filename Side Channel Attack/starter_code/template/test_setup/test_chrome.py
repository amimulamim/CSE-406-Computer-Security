#!/usr/bin/env python3
import sys
import subprocess
import time
import socket
import shutil

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

FINGERPRINTING_URL = "http://127.0.0.1:5000"
PORT = 5000

def wait_for_server(port, timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        sock = socket.socket()
        if sock.connect_ex(("127.0.0.1", port)) == 0:
            sock.close()
            return True
        sock.close()
        time.sleep(0.5)
    return False

def main():
    # 1) start your Flask app
    server = subprocess.Popen([sys.executable, "app.py"])
    try:
        # 2) wait for it
        if not wait_for_server(PORT):
            print(f"❌ Flask didn’t start on port {PORT}", file=sys.stderr)
            sys.exit(1)
        print(f"✅ Flask is up at {FINGERPRINTING_URL}")

        # 3) test if Chrome is available
        chrome_path = shutil.which("google-chrome")
        if not chrome_path:
            print("❌ google-chrome not found on PATH", file=sys.stderr)
            sys.exit(1)
        print(f"✅ Using Chrome wrapper at: {chrome_path}")

        # 4) use the system chromedriver
        driver_path = shutil.which("chromedriver")
        if not driver_path:
            print("❌ chromedriver not found on PATH", file=sys.stderr)
            sys.exit(1)
        print(f"✅ Using ChromeDriver at: {driver_path}")

        # 5) launch Selenium
        opts = Options()
        # Don't specify binary location, let it auto-detect
        opts.add_argument("--window-size=1920,1080")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--disable-extensions")
        opts.add_argument("--headless")  # Enable headless mode for testing
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=opts)

        # 6) smoke-test
        driver.get(FINGERPRINTING_URL)
        print("🌐 Page title is:", driver.title)
        driver.quit()

    finally:
        # 7) tear down
        server.terminate()
        server.wait()

if __name__ == "__main__":
    main()
