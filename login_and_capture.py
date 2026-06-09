import json
import os
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
    print("Launching chrome...")
    browser = p.chromium.launch(headless=True, channel="chrome")
    context = browser.new_context(
        viewport={"width": 1280, "height": 720},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    context.add_cookies(playwright_cookies)
    
    page = context.new_page()
    
    tokens = []
    
    def monitor_response(res):
        url = res.url
        status = res.status
        if "rownd.io" in url or "stardust.app" in url:
            print(f"[Captured] Status {status}: {url}")
            if "token" in url or "auth" in url:
                try:
                    text = res.text()
                    print(f"  Body snippet: {text[:500]}")
                    data = json.loads(text)
                    for key in ["access_token", "token"]:
                        if key in data:
                            tokens.append(data[key])
                        elif "auth" in data and key in data["auth"]:
                            tokens.append(data["auth"][key])
                except Exception as e:
                    print(f"  Error reading token body: {e}")
                    
    page.on("response", monitor_response)
    
    print("Pre-warming Google session...")
    page.goto("https://contacts.google.com/", wait_until="load")
    time.sleep(3)
    
    print("Navigating to Vercel site to set localStorage context...")
    page.goto("https://denngay.vercel.app/", wait_until="commit")
    page.evaluate("() => localStorage.setItem('rph_state', JSON.stringify({ app: { id: '337080849221550671' } }))")
    
    print("Navigating fully to denngay.vercel.app...")
    page.goto("https://denngay.vercel.app/", wait_until="load")
    time.sleep(3)
    
    print("Clicking login button...")
    # Wait for the login button to be visible
    login_btn = page.locator("text=Đăng nhập bằng Google")
    if login_btn.count() > 0:
        # Expect a popup when clicking
        with context.expect_page() as popup_info:
            login_btn.click()
        popup_page = popup_info.value
        print(f"Popup opened. Title: {popup_page.title()} URL: {popup_page.url}")
        
        # Listen for responses in the popup context
        popup_page.on("response", monitor_response)
        
        # Wait for the popup to complete redirection and close
        print("Waiting for popup to finish authentication...")
        for _ in range(30):
            if popup_page.is_closed():
                print("Popup closed successfully.")
                break
            time.sleep(1)
        else:
            print(f"Popup did not close after 30 seconds. Current URL: {popup_page.url}")
            # Take popup screenshot
            popup_page.screenshot(path=r"C:\Users\PC\Desktop\nhacuongthuoc\popup_stuck.png")
            print("Saved popup stuck screenshot.")
    else:
        print("Login button not found on the page!")
        
    print("Checking main page state...")
    time.sleep(5)
    page.screenshot(path=r"C:\Users\PC\Desktop\nhacuongthuoc\main_page_after_login.png")
    print(f"Main page URL: {page.url}")
    print(f"Tokens captured: {len(tokens)}")
    if tokens:
        print(f"Captured access token: {tokens[0]}")
        # Call Stardust API directly from python using the token
        import httpx
        headers = {
            'Authorization': f'Bearer {tokens[0]}',
            'User-Agent': 'Stardust/5.21.0 (Android; SDK 33)',
            'Accept': 'application/json'
        }
        r = httpx.get('https://api.stardust.app/api/v2/my-logs', headers=headers)
        print(f"Stardust API Response Status: {r.status_code}")
        if r.status_code == 200:
            print("Stardust API Call Success!")
            logs_data = r.json()
            # Write to a file
            with open(r"C:\Users\PC\Desktop\nhacuongthuoc\stardust_logs_direct.json", "w", encoding="utf-8") as f_out:
                json.dump(logs_data, f_out, indent=2, ensure_ascii=False)
            logs = logs_data if isinstance(logs_data, list) else (logs_data.get('logs', []) or logs_data.get('data', []))
            period_dates = sorted([log['date'] for log in logs if log.get('period') or log.get('bleeding') or (log.get('flow') and log.get('flow') != 'none')])
            print(f"Total period days logged: {len(period_dates)}")
            if period_dates:
                print("Last 15 period dates:")
                for d in period_dates[-15:]:
                    print(f"  {d}")
        else:
            print(f"Stardust API Error Payload: {r.text}")
            
    browser.close()
