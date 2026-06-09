import json
import os
import sys
import httpx
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
    browser = p.chromium.launch(headless=True, channel="chrome")
    context = browser.new_context()
    context.add_cookies(playwright_cookies)
    page = context.new_page()
    
    print("Navigating to Google Contacts to fetch email...")
    page.goto("https://contacts.google.com/", wait_until="load")
    
    # Extract email from page
    # In contacts, the user's profile image or profile container usually has their email or name
    # Let's inspect the page html or evaluate javascript
    email = page.evaluate("() => { return document.body.innerHTML.match(/[a-zA-Z0-9._%+-]+@gmail\\.com/)?.[0] || 'not found' }")
    print("Found potential email:", email)
    
    # Try another way: checking the page title or other headers
    # Let's also check if there is an avatar button with an aria-label containing the email
    avatar = page.locator("a[href*='accounts.google.com/SignOutOptions']")
    if avatar.count() > 0:
        print("Avatar aria-label:", label.encode('ascii', 'ignore').decode('ascii'))
        
    browser.close()
