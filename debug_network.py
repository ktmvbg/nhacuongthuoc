import json
import os
import sys
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
    context = browser.new_context()
    context.add_cookies(playwright_cookies)
    
    page = context.new_page()
    
    # Intercept network requests
    page.on("request", lambda req: print(f"Request: {req.method} {req.url}"))
    page.on("response", lambda res: print(f"Response: {res.status} {res.url}"))
    page.on("console", lambda msg: print(f"Console: {msg.type}: {msg.text}"))
    
    print("Pre-warming Google...")
    page.goto("https://contacts.google.com/", wait_until="networkidle")
    
    print("\n--- Navigating to denngay ---")
    page.goto("https://denngay.vercel.app/", wait_until="networkidle")
    
    print("\n--- Clicking Google login button ---")
    google_btn = page.locator("button:has-text('Đăng nhập bằng Google')")
    if google_btn.count() > 0:
        try:
            with context.expect_page(timeout=5000) as new_page_info:
                google_btn.click()
            popup = new_page_info.value
            print(f"Popup opened: {popup.url}")
        except Exception as e:
            print(f"Failed click/popup: {e}")
            
    browser.close()
