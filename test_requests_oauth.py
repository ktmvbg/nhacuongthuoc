import json
import os
import sys
import httpx

cookies_path = r"c:\Users\PC\Desktop\nhacuongthuoc\cookies.txt"

if not os.path.exists(cookies_path):
    print(f"Error: cookies.txt not found at {cookies_path}")
    sys.exit(1)

with open(cookies_path, "r", encoding="utf-8") as f:
    raw_cookies = json.load(f)

# Convert cookies to dictionary for httpx
cookies = {}
for cookie in raw_cookies:
    if cookie.get("domain") in [".google.com", "accounts.google.com"]:
        cookies[cookie["name"]] = cookie["value"]

print(f"Loaded {len(cookies)} Google cookies.")

client = httpx.Client(
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive"
    },
    cookies=cookies,
    follow_redirects=False
)

# Test warming up
try:
    r = client.get("https://contacts.google.com/")
    print(f"Warm up contacts.google.com status: {r.status_code}")
except Exception as e:
    print(f"Warm up failed: {e}")

oauth_url = (
    "https://accounts.google.com/o/oauth2/v2/auth?"
    "client_id=442565757208-2fk8nhdbnk679hkqvmtthsvt1p4bbpmu.apps.googleusercontent.com&"
    "redirect_uri=https%3A%2F%2Fapi.rownd.io%2Fhub%2Fauth%2Fgoogle%2Fcallback&"
    "response_type=code&"
    "scope=openid+email+profile&"
    "state=12345"
)

print("\n--- Making request to Google OAuth ---")
try:
    r = client.get(oauth_url)
    print(f"Status: {r.status_code}")
    print(f"Headers: {dict(r.headers)}")
    if "location" in r.headers:
        print(f"Redirect Location: {r.headers['location']}")
    else:
        # Print a bit of body
        print(f"Body: {r.text[:1000]}")
except Exception as e:
    print(f"OAuth request failed: {e}")
