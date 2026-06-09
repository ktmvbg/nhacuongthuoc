import json
import os
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
    
    def handle_request(req):
        if "rownd.io" in req.url or "auth" in req.url:
            print(f"[Request] {req.method} {req.url}")
            try:
                post_data = req.post_data
                if post_data:
                    print(f"  Post Data: {post_data[:1000]}")
            except Exception:
                pass

    def handle_response(res):
        if "rownd.io" in res.url or "auth" in res.url:
            print(f"[Response] {res.status} {res.url}")
            try:
                # Print headers and body
                content_type = res.headers.get("content-type", "")
                if "application/json" in content_type or "text" in content_type:
                    body = res.text()
                    print(f"  Body (first 1000 chars): {body[:1000]}")
            except Exception as e:
                print(f"  Error reading response: {e}")
                
    page.on("request", handle_request)
    page.on("response", handle_response)
    
    print("Pre-warming Google session...")
    page.goto("https://contacts.google.com/", wait_until="load")
    time.sleep(3)
    
    print("Navigating to Vercel site to set localStorage context...")
    page.goto("https://denngay.vercel.app/", wait_until="commit")
    
    # We will set BOTH app keys to test:
    # 1. Stardust App ID: 337080849221550671
    page.evaluate("() => localStorage.setItem('rph_state', JSON.stringify({ app: { id: '337080849221550671' } }))")
    
    print("Navigating fully to denngay.vercel.app...")
    page.goto("https://denngay.vercel.app/", wait_until="load")
    
    print("Waiting 15 seconds for responses...")
    time.sleep(15)
    
    browser.close()
