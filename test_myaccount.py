import json
import os
import sys
import httpx

cookies_path = r"c:\Users\PC\Desktop\nhacuongthuoc\cookies.txt"

with open(cookies_path, "r", encoding="utf-8") as f:
    raw_cookies = json.load(f)

cookies = {}
for cookie in raw_cookies:
    if cookie.get("domain") in [".google.com", "accounts.google.com", "myaccount.google.com"]:
        cookies[cookie["name"]] = cookie["value"]

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

try:
    r = client.get("https://myaccount.google.com/")
    print(f"myaccount.google.com status: {r.status_code}")
    print(f"Location header: {r.headers.get('location')}")
except Exception as e:
    print(f"Error: {e}")
