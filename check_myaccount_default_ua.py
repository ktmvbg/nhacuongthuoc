import json
import time
import sys
# Configure UTF-8 stdout
sys.stdout.reconfigure(encoding='utf-8')
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
    print("Launching chrome with default user agent...")
    browser = p.chromium.launch(headless=True, channel="chrome")
    context = browser.new_context(
        viewport={"width": 1280, "height": 720}
    )
    context.add_cookies(playwright_cookies)
    
    page = context.new_page()
    
    print("Default user agent:", page.evaluate("() => navigator.userAgent"))
    
    print("Navigating to Contacts first...")
    page.goto("https://contacts.google.com/", wait_until="load")
    time.sleep(2)
    print("Contacts Page Title:", page.title())
    
    print("Navigating to My Account...")
    page.goto("https://myaccount.google.com/", wait_until="load")
    time.sleep(3)
    
    print("Final URL:", page.url)
    print("Page Title:", page.title())
    
    body_text = page.evaluate("() => document.body.innerText")
    print("\n--- MYACCOUNT PAGE TEXT ---")
    print(body_text[:1000])
    print("---------------------------\n")
    
    browser.close()
