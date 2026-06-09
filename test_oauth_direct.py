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
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    context.add_cookies(playwright_cookies)
    
    page = context.new_page()
    
    # Intercept network requests to log redirects
    page.on("request", lambda req: print(f"Req: {req.method} {req.url}"))
    page.on("response", lambda res: print(f"Res: {res.status} {res.url}"))
    
    print("Pre-warming Google session...")
    page.goto("https://contacts.google.com/", wait_until="networkidle")
    
    # Direct Google OAuth authorization endpoint for Stardust
    # Redirect URI is Stardust's Rownd callback
    oauth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        "client_id=442565757208-2fk8nhdbnk679hkqvmtthsvt1p4bbpmu.apps.googleusercontent.com&"
        "redirect_uri=https%3A%2F%2Fapi.rownd.io%2Fhub%2Fauth%2Fgoogle%2Fcallback&"
        "response_type=code&"
        "scope=openid+email+profile&"
        "state=12345"
    )
    
    print("\n--- Navigating to Google OAuth URL ---")
    page.goto(oauth_url, wait_until="networkidle")
    
    print("\nFinal URL after redirects:", page.url)
    print("Page Title:", page.title())
    
    # Take a screenshot to see if there is a consent screen or if we got blocked
    page.screenshot(path="C:\\Users\\PC\\.gemini\\antigravity-ide\\brain\\98487492-efcc-4a4a-9527-94f16c05be12\\oauth_state.png")
    print("Screenshot saved.")
    
    browser.close()
