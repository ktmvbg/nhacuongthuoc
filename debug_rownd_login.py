import json
import os
import sys
import time
from playwright.sync_api import sync_playwright

cookies_path = r"c:\Users\PC\Desktop\nhacuongthuoc\cookies.txt"

if not os.path.exists(cookies_path):
    print(f"Error: cookies.txt not found at {cookies_path}")
    sys.exit(1)

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
    same_site = cookie.get("sameSite")
    if same_site:
        same_site_cap = same_site.lower().capitalize()
        if same_site_cap in ["Lax", "None", "Strict"]:
            pw_cookie["sameSite"] = same_site_cap
    if expires is not None:
        pw_cookie["expires"] = float(expires)
    playwright_cookies.append(pw_cookie)

with sync_playwright() as p:
    print("Launching headless chrome...")
    browser = p.chromium.launch(headless=True, channel="chrome")
    
    # Create context and load Google cookies
    context = browser.new_context(
        viewport={"width": 1280, "height": 720},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    context.add_cookies(playwright_cookies)
    
    page = context.new_page()
    
    # Listen to console messages
    page.on("console", lambda msg: print(f"[Console] {msg.type}: {msg.text}"))
    page.on("pageerror", lambda err: print(f"[PageError] {err}"))
    
    # Go to contacts first to ensure session is warm
    print("Pre-warming Google session...")
    page.goto("https://contacts.google.com/", wait_until="networkidle")
    
    # Go to the deployed site
    print("Navigating to https://denngay.vercel.app/ ...")
    page.goto("https://denngay.vercel.app/", wait_until="networkidle")
    print("Page Title:", page.title())
    
    # Take initial screenshot
    page.screenshot(path="C:\\Users\\PC\\.gemini\\antigravity-ide\\brain\\98487492-efcc-4a4a-9527-94f16c05be12\\denngay_loaded_1.png")
    
    # Find Google Login button and click it
    google_btn = page.locator("button:has-text('Đăng nhập bằng Google')")
    if google_btn.count() == 0:
        print("Google login button not found! Maybe already logged in?")
        # Check if stardust session exists in localStorage
        session_val = page.evaluate("() => localStorage.getItem('stardust_session')")
        print("localStorage stardust_session:", session_val)
    else:
        print("Clicking Google login button...")
        # Since it might trigger a popup, let's watch for the popup
        with context.expect_page() as new_page_info:
            google_btn.click()
        
        popup = new_page_info.value
        print("Popup opened. URL:", popup.url)
        popup.on("console", lambda msg: print(f"[Popup Console] {msg.type}: {msg.text}"))
        popup.on("pageerror", lambda err: print(f"[Popup PageError] {err}"))
        
        # Wait for redirect or popup closure
        print("Waiting for popup flow to complete...")
        for i in range(15):
            time.sleep(1)
            print(f"Seconds elapsed: {i+1}, Popup URL: {popup.url if not popup.is_closed() else 'CLOSED'}, Main URL: {page.url}")
            # Check if main page localstorage now has the token
            session_val = page.evaluate("() => localStorage.getItem('stardust_session')")
            if session_val:
                print("SUCCESS! localStorage stardust_session:", session_val)
                break
        
        # Take screenshot of both pages if open
        if not popup.is_closed():
            popup.screenshot(path="C:\\Users\\PC\\.gemini\\antigravity-ide\\brain\\98487492-efcc-4a4a-9527-94f16c05be12\\popup_state.png")
            popup.close()
            
    page.screenshot(path="C:\\Users\\PC\\.gemini\\antigravity-ide\\brain\\98487492-efcc-4a4a-9527-94f16c05be12\\denngay_final.png")
    
    # Let's print localStorage again
    session_val = page.evaluate("() => localStorage.getItem('stardust_session')")
    print("Final localStorage stardust_session:", session_val)
    
    browser.close()
