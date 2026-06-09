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
    
    # Intercept network requests to log redirects
    page.on("request", lambda req: print(f"Req: {req.method} {req.url}"))
    page.on("response", lambda res: print(f"Res: {res.status} {res.url}"))
    
    print("Pre-warming Google session...")
    page.goto("https://contacts.google.com/", wait_until="load")
    time.sleep(3)
    
    oauth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        "client_id=442565757208-2fk8nhdbnk679hkqvmtthsvt1p4bbpmu.apps.googleusercontent.com&"
        "redirect_uri=https%3A%2F%2Fapi.rownd.io%2Fhub%2Fauth%2Fgoogle%2Fcallback&"
        "response_type=code&"
        "scope=openid+email+profile&"
        "state=12345"
    )
    
    print("\n--- Navigating to Google OAuth URL ---")
    page.goto(oauth_url, wait_until="load")
    time.sleep(5)
    
    print("\nPage URL:", page.url)
    print("Page Title:", page.title())
    
    page.screenshot(path="C:\\Users\\PC\\.gemini\\antigravity-ide\\brain\\98487492-efcc-4a4a-9527-94f16c05be12\\oauth_signin.png")
    
    # Check if there is an account chooser list (e.g. element with role="link" or text containing user's email/name)
    # Commonly, Google lists signed-in accounts using `div[data-email]` or `li` elements or listbox items.
    # Let's inspect the page content for any clickable profile list elements
    print("\nChecking if account chooser is present...")
    account_elements = page.locator("[data-email]")
    print(f"Found {account_elements.count()} elements with data-email attribute.")
    
    if account_elements.count() > 0:
        email = account_elements.first.get_attribute("data-email")
        print(f"Clicking first account in list: {email}")
        account_elements.first.click()
        time.sleep(5)
        print("URL after clicking account:", page.url)
        page.screenshot(path="C:\\Users\\PC\\.gemini\\antigravity-ide\\brain\\98487492-efcc-4a4a-9527-94f16c05be12\\oauth_final.png")
    else:
        # Check if there are other selectors (e.g. div with jsname="Lgbsbe" or containing text/link of the account)
        # We can try to look for links containing "@gmail.com" or similar
        print("Data-email elements not found. Checking general clickable selectors...")
        # Google account chooser lists have links or buttons
        gmail_links = page.locator("div[role='link'], div[role='button'], a")
        gmail_match = None
        for i in range(gmail_links.count()):
            text = gmail_links.nth(i).inner_text()
            if "@" in text or "gmail" in text.lower():
                print(f"Found potential account option {i}: '{text}'")
                gmail_match = gmail_links.nth(i)
                break
        if gmail_match:
            print("Clicking found account element...")
            gmail_match.click()
            time.sleep(5)
            print("URL after click:", page.url)
            page.screenshot(path="C:\\Users\\PC\\.gemini\\antigravity-ide\\brain\\98487492-efcc-4a4a-9527-94f16c05be12\\oauth_final.png")
        else:
            print("No accounts listed or found on screen.")
            
    browser.close()
