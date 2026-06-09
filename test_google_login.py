import json
import os
import sys
from playwright.sync_api import sync_playwright

cookies_path = r"c:\Users\PC\Desktop\nhacuongthuoc\cookies.txt"

if not os.path.exists(cookies_path):
    print(f"Error: cookies.txt not found at {cookies_path}")
    sys.exit(1)

with open(cookies_path, "r", encoding="utf-8") as f:
    raw_cookies = json.load(f)

# Convert cookies to Playwright format
playwright_cookies = []
for cookie in raw_cookies:
    # Playwright expects expires as float (unix timestamp), not expirationDate
    expires = cookie.get("expirationDate")
    # Clean cookie object
    pw_cookie = {
        "name": cookie["name"],
        "value": cookie["value"],
        "domain": cookie["domain"],
        "path": cookie["path"],
        "secure": cookie.get("secure", True),
        "httpOnly": cookie.get("httpOnly", False),
    }
    # sameSite must be one of 'Lax', 'None', 'Strict' (capitalized) or omitted
    same_site = cookie.get("sameSite")
    if same_site:
        same_site_cap = same_site.lower().capitalize()
        if same_site_cap in ["Lax", "None", "Strict"]:
            pw_cookie["sameSite"] = same_site_cap
    if expires is not None:
        pw_cookie["expires"] = float(expires)
    
    playwright_cookies.append(pw_cookie)

print(f"Loaded {len(playwright_cookies)} cookies.")

with sync_playwright() as p:
    # Use native chrome channel if available to match browser fingerprint
    print("Launching browser...")
    browser = p.chromium.launch(headless=True, channel="chrome")
    context = browser.new_context()
    
    # Add cookies to the context
    context.add_cookies(playwright_cookies)
    
    page = context.new_page()
    print("Navigating to https://contacts.google.com/ ...")
    page.goto("https://contacts.google.com/", wait_until="networkidle")
    
    print("Page title:", page.title())
    print("Current URL:", page.url)
    
    # Save a screenshot to the brain folder for verification (invisible to user, but stored)
    screenshot_path = r"C:\Users\PC\.gemini\antigravity-ide\brain\98487492-efcc-4a4a-9527-94f16c05be12\playwright_contacts.png"
    page.screenshot(path=screenshot_path)
    print(f"Screenshot saved to {screenshot_path}")
    
    browser.close()
