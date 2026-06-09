import json
import os
import sys
import time
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
    print("Launching chrome...")
    browser = p.chromium.launch(headless=True, channel="chrome")
    context = browser.new_context(
        viewport={"width": 1280, "height": 720},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    context.add_cookies(playwright_cookies)
    
    page = context.new_page()
    
    tokens = []
    
    def handle_response(res):
        if "auth/instant" in res.url:
            print(f"Rownd Instant Auth Status: {res.status}")
            try:
                text = res.text()
                data = json.loads(text)
                if "access_token" in data:
                    tokens.append(data["access_token"])
                    print("SUCCESS: Captured Access Token from Instant Auth!")
            except Exception as e:
                print(f"Error reading instant auth: {e}")
                
    page.on("response", handle_response)
    page.on("console", lambda msg: print(f"Page Console: {msg.text}"))
    
    print("Pre-warming Google session...")
    page.goto("https://contacts.google.com/", wait_until="load")
    time.sleep(3)
    
    # Pre-populate localStorage to avoid the Missing app id error
    print("Navigating to Vercel site to set localStorage context...")
    page.goto("https://denngay.vercel.app/", wait_until="commit")
    page.evaluate("() => localStorage.setItem('rph_state', JSON.stringify({ app: { id: '337080849221550671' } }))")
    
    print("Navigating fully to denngay.vercel.app...")
    page.goto("https://denngay.vercel.app/", wait_until="networkidle")
    time.sleep(10)
    
    if tokens:
        token = tokens[0]
        print(f"\nRownd Access Token: {token[:50]}...")
        
        # Call Stardust API
        print("Calling Stardust API...")
        headers = {
            'Authorization': f'Bearer {token}',
            'User-Agent': 'Stardust/5.21.0 (Android; SDK 33)',
            'Accept': 'application/json'
        }
        try:
            r = httpx.get('https://api.stardust.app/api/v2/my-logs', headers=headers)
            print(f"Stardust API Status: {r.status_code}")
            if r.status_code == 200:
                logs_data = r.json()
                print("\n=== STARDUST LOGS RECEIVED! ===")
                # Save logs data to a file for review
                out_path = r"C:\Users\PC\.gemini\antigravity-ide\brain\98487492-efcc-4a4a-9527-94f16c05be12\scratch\stardust_logs.json"
                with open(out_path, "w", encoding="utf-8") as f_out:
                    json.dump(logs_data, f_out, indent=2, ensure_ascii=False)
                print(f"Saved logs to {out_path}")
                
                # Extract some period dates to display
                logs = logs_data if isinstance(logs_data, list) else (logs_data.get('logs', []) or logs_data.get('data', []))
                period_dates = sorted([log['date'] for log in logs if log.get('period') or log.get('bleeding') or (log.get('flow') and log.get('flow') != 'none')])
                print(f"Total period days logged: {len(period_dates)}")
                print(f"First logged period date: {period_dates[0] if period_dates else 'N/A'}")
                print(f"Last logged period date: {period_dates[-1] if period_dates else 'N/A'}")
            else:
                print(f"Error payload: {r.text}")
        except Exception as e:
            print(f"API request error: {e}")
    else:
        print("Instant auth did not return a token.")
        
    browser.close()
