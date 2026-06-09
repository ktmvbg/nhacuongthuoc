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
    
    # Intercept network requests and responses
    tokens_captured = []
    
    def handle_request(req):
        if "rownd.io" in req.url:
            print(f"[Rownd Request] {req.method} {req.url}")
            if req.post_data:
                print(f"  Post Data: {req.post_data}")
                
    def handle_response(res):
        if "rownd.io" in res.url:
            print(f"[Rownd Response] {res.status} {res.url}")
            try:
                # If it's a JSON response, print it to find the token
                content_type = res.headers.get("content-type", "")
                if "application/json" in content_type:
                    text = res.text()
                    print(f"  JSON: {text[:1000]}")
                    if "access_token" in text:
                        data = json.loads(text)
                        if "access_token" in data:
                            tokens_captured.append(data["access_token"])
                            print("\n*** CAPTURED ACCESS TOKEN! ***\n")
            except Exception as e:
                pass
                
    page.on("request", handle_request)
    page.on("response", handle_response)
    
    print("Pre-warming Google session...")
    page.goto("https://contacts.google.com/", wait_until="load")
    time.sleep(3)
    
    oauth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        "client_id=442565757208-2fk8nhdbnk679hkqvmtthsvt1p4bbpmu.apps.googleusercontent.com&"
        "redirect_uri=https%3A%2F%2Fapi.rownd.io%2Fhub%2Fauth%2Fgoogle%2Fcallback&"
        "response_type=code&"
        "scope=openid+email+profile&"
        "state=12345&"
        "login_hint=rbkya2013@gmail.com"
    )
    
    print("\n--- Navigating to Google OAuth URL with login_hint ---")
    page.goto(oauth_url, wait_until="load")
    time.sleep(5)
    
    print("\nFinal URL:", page.url)
    print("Page Title:", page.title())
    
    # Save a screenshot to see if it succeeded or got stuck
    page.screenshot(path="C:\\Users\\PC\\.gemini\\antigravity-ide\\brain\\98487492-efcc-4a4a-9527-94f16c05be12\\oauth_hint_final.png")
    
    if tokens_captured:
        print(f"Successfully captured {len(tokens_captured)} token(s)!")
        # Save token to a file
        token_path = r"C:\Users\PC\.gemini\antigravity-ide\brain\98487492-efcc-4a4a-9527-94f16c05be12\scratch\rownd_token.txt"
        with open(token_path, "w") as f:
            f.write(tokens_captured[0])
        print(f"Saved token to {token_path}")
    else:
        print("No tokens captured.")
        
    browser.close()
