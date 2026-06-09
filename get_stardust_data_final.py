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
    
    captured_responses = []
    
    def handle_response(res):
        if "rownd.io" in res.url:
            url = res.url
            status = res.status
            try:
                text = res.text()
                # Store URL, Status, and Body
                captured_responses.append({
                    "url": url,
                    "status": status,
                    "body": text
                })
                print(f"[Captured Rownd API] {status} {url}")
            except Exception as e:
                pass
                
    page.on("response", handle_response)
    
    print("Pre-warming Google session...")
    page.goto("https://contacts.google.com/", wait_until="load")
    time.sleep(3)
    
    print("Navigating to Vercel site to set localStorage context...")
    page.goto("https://denngay.vercel.app/", wait_until="commit")
    page.evaluate("() => localStorage.setItem('rph_state', JSON.stringify({ app: { id: '337080849221550671' } }))")
    
    print("Navigating fully to denngay.vercel.app...")
    page.goto("https://denngay.vercel.app/", wait_until="load")
    
    print("Waiting 15 seconds for Rownd silent authentication to complete...")
    time.sleep(15)
    
    # Save all captured responses to review
    out_path = r"C:\Users\PC\.gemini\antigravity-ide\brain\98487492-efcc-4a4a-9527-94f16c05be12\scratch\rownd_responses.json"
    with open(out_path, "w", encoding="utf-8") as f_out:
        json.dump(captured_responses, f_out, indent=2, ensure_ascii=False)
    print(f"Saved all captured Rownd responses to {out_path}")
    
    # Look for access token in captured responses
    access_token = None
    for item in captured_responses:
        body_text = item["body"]
        if "access_token" in body_text:
            try:
                data = json.loads(body_text)
                # Check nested structures
                if "access_token" in data:
                    access_token = data["access_token"]
                elif "auth" in data and "access_token" in data["auth"]:
                    access_token = data["auth"]["access_token"]
                elif isinstance(data, dict):
                    # Recursive search
                    def find_token(obj):
                        if isinstance(obj, dict):
                            if "access_token" in obj:
                                return obj["access_token"]
                            for k, v in obj.items():
                                res = find_token(v)
                                if res:
                                    return res
                        return None
                    access_token = find_token(data)
                
                if access_token:
                    print(f"\n*** FOUND ACCESS TOKEN in response from: {item['url']} ***")
                    break
            except Exception as e:
                pass
                
    if access_token:
        # Save token
        token_path = r"C:\Users\PC\.gemini\antigravity-ide\brain\98487492-efcc-4a4a-9527-94f16c05be12\scratch\rownd_token.txt"
        with open(token_path, "w") as f:
            f.write(access_token)
        print(f"Saved token to {token_path}")
        
        # Call Stardust API
        print("Calling Stardust API...")
        headers = {
            'Authorization': f'Bearer {access_token}',
            'User-Agent': 'Stardust/5.21.0 (Android; SDK 33)',
            'Accept': 'application/json'
        }
        r = httpx.get('https://api.stardust.app/api/v2/my-logs', headers=headers)
        print(f"Stardust API Status: {r.status_code}")
        if r.status_code == 200:
            logs_data = r.json()
            logs_path = r"C:\Users\PC\.gemini\antigravity-ide\brain\98487492-efcc-4a4a-9527-94f16c05be12\scratch\stardust_logs.json"
            with open(logs_path, "w", encoding="utf-8") as f_out:
                json.dump(logs_data, f_out, indent=2, ensure_ascii=False)
            print(f"Saved logs to {logs_path}")
            
            # Print statistics
            logs = logs_data if isinstance(logs_data, list) else (logs_data.get('logs', []) or logs_data.get('data', []))
            period_dates = sorted([log['date'] for log in logs if log.get('period') or log.get('bleeding') or (log.get('flow') and log.get('flow') != 'none')])
            print(f"Total period days logged: {len(period_dates)}")
            if period_dates:
                print(f"Period dates: {', '.join(period_dates[-10:])} (showing last 10)")
        else:
            print(f"API Error Payload: {r.text}")
    else:
        print("Could not find access token in any Rownd API response.")
        
    browser.close()
