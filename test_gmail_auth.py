import json
import os
import sys
import httpx

cookies_path = r"c:\Users\PC\Desktop\nhacuongthuoc\cookies.txt"

with open(cookies_path, "r", encoding="utf-8") as f:
    raw_cookies = json.load(f)

cookies = {}
for cookie in raw_cookies:
    if cookie.get("domain") in [".google.com", "accounts.google.com"]:
        cookies[cookie["name"]] = cookie["value"]

client = httpx.Client(
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive"
    },
    cookies=cookies,
    follow_redirects=True
)

url = (
    "https://accounts.google.com/o/oauth2/v2/auth?"
    "client_id=442565757208-2fk8nhdbnk679hkqvmtthsvt1p4bbpmu.apps.googleusercontent.com&"
    "redirect_uri=https%3A%2F%2Fapi.rownd.io%2Fhub%2Fauth%2Fgoogle%2Fcallback&"
    "response_type=code&"
    "scope=openid+email+profile&"
    "state=12345"
)

try:
    r = client.get(url)
    print(f"Final URL: {r.url}")
    print(f"Final Status: {r.status_code}")
    # Search for login/password or check if it redirected to rownd.io
    if "api.rownd.io" in str(r.url):
        print("SUCCESS! Redirected to rownd.io callback!")
    else:
        print("Failed to authenticate directly. Need verification.")
except Exception as e:
    print(f"Error: {e}")
