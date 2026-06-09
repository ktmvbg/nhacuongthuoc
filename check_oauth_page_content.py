import json
import os
import time
import sys
import urllib.parse

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

client_id = "900415098360-ritfis4563e74sluvre9nsmhi2oa4uf0.apps.googleusercontent.com"
redirect_uri = "https://denngay.vercel.app"
scope = "openid email profile"
nonce = "stardust_test_12345"
oauth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&redirect_uri={urllib.parse.quote(redirect_uri)}&response_type=id_token&scope={scope.replace(' ', '+')}&nonce={nonce}"

with sync_playwright() as p:
    print("Launching chrome...")
    browser = p.chromium.launch(headless=True, channel="chrome")
    context = browser.new_context(
        viewport={"width": 1280, "height": 720},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    context.add_cookies(playwright_cookies)
    
    page = context.new_page()
    
    # Listen to responses to see if id_token is returned during redirections
    captured_urls = []
    page.on("response", lambda res: captured_urls.append(res.url))
    
    print("Pre-warming Google session on Contacts...")
    page.goto("https://contacts.google.com/", wait_until="load")
    time.sleep(3)
    
    print("Navigating to Custom Google OAuth URL...")
    page.goto(oauth_url, wait_until="load")
    time.sleep(5)
    
    print("Current URL:", page.url)
    print("Page Title:", page.title())
    
    # Print all text content to find email
    body_text = page.evaluate("() => document.body.innerText")
    print("\n--- PAGE TEXT CONTENT ---")
    print(body_text[:2000])
    print("-------------------------\n")
    
    # Check if user email is present on screen
    email_selector = "text=rbkya2013@gmail.com"
    count = page.locator(email_selector).count()
    print(f"Occurrences of 'rbkya2013@gmail.com': {count}")
    
    if count > 0:
        print("Clicking the user account element...")
        page.locator(email_selector).first.click()
        print("Clicked! Waiting 10 seconds for redirects...")
        time.sleep(10)
        print("Final URL after clicking account:", page.url)
        # Take screenshot after click
        page.screenshot(path=r"C:\Users\PC\Desktop\nhacuongthuoc\oauth_after_click.png")
    else:
        # Check if there is any other account element or button
        print("Email text not found. Checking for general account chooser or sign-in buttons...")
        # Check buttons or options
        buttons = page.locator("button, [role='button']").all()
        print(f"Found {len(buttons)} button-like elements:")
        for idx, btn in enumerate(buttons[:10]):
            try:
                print(f"  [{idx}] text='{btn.inner_text()}' role='{btn.get_attribute('role')}' id='{btn.get_attribute('id')}'")
            except:
                pass
                
    browser.close()
