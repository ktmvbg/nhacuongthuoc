import json
import os
import sys
import time
from playwright.sync_api import sync_playwright

cookies_path = r"c:\Users\PC\Desktop\nhacuongthuoc\cookies.txt"

with open(cookies_path, "r", encoding="utf-8") as f:
    raw_cookies = json.load(f)

playwright_cookies = []
for cookie in raw_cookies:
    expires = cookie.get("expirationDate")
    pw_cookie = {
        "name": cookie["name"],
        "value": cookie["value"],
        "domain": cookie["domain"],
        "path": cookie["path"],
        "secure": cookie.get("secure", True),
        "httpOnly": cookie.get("httpOnly", False),
    }
    if expires is not None:
        pw_cookie["expires"] = float(expires)
    playwright_cookies.append(pw_cookie)

with sync_playwright() as p:
    print("Launching chrome...")
    browser = p.chromium.launch(headless=True, channel="chrome")
    context = browser.new_context(
        viewport={"width": 1280, "height": 720},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    context.add_cookies(playwright_cookies)
    
    page = context.new_page()
    
    def handle_response(res):
        if "auth/instant" in res.url:
            print(f"\nURL: {res.url}")
            print(f"Status: {res.status}")
            print(f"Headers: {dict(res.headers)}")
            try:
                print(f"Body: {res.text()[:2000]}")
            except Exception as e:
                print(f"Error reading body: {e}")
                
    page.on("response", handle_response)
    page.on("console", lambda msg: print(f"Page Console: {msg.text}"))
    
    print("Pre-warming Google session...")
    page.goto("https://contacts.google.com/", wait_until="load")
    time.sleep(3)
    
    print("Navigating to Vercel site to set localStorage context...")
    page.goto("https://denngay.vercel.app/", wait_until="commit")
    page.evaluate("() => localStorage.setItem('rph_state', JSON.stringify({ app: { id: '337080849221550671' } }))")
    
    print("Navigating fully to denngay.vercel.app...")
    page.goto("https://denngay.vercel.app/", wait_until="load")
    time.sleep(10)
    
    browser.close()
