import json
import os
import time
import sys
import urllib.parse
import httpx
from playwright.sync_api import sync_playwright

# Configure UTF-8 stdout
sys.stdout.reconfigure(encoding='utf-8')

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
    print("Launching chrome with stealth args...")
    browser = p.chromium.launch(
        headless=True,
        channel="chrome",
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--no-sandbox"
        ]
    )
    context = browser.new_context(
        viewport={"width": 1280, "height": 720},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    context.add_cookies(playwright_cookies)
    
    # Hide webdriver flag via init script
    context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    page = context.new_page()
    
    print("Pre-warming Google session on Contacts...")
    page.goto("https://contacts.google.com/", wait_until="load")
    time.sleep(3)
    print("Contacts Page Title:", page.title())
    
    print("Navigating to Custom Google OAuth URL...")
    page.goto(oauth_url, wait_until="load")
    time.sleep(5)
    
    final_url = page.url
    print("Final URL:", final_url)
    print("Page Title:", page.title())
    
    # Save a screenshot
    screenshot_path = r"C:\Users\PC\Desktop\nhacuongthuoc\oauth_stealth_result.png"
    page.screenshot(path=screenshot_path)
    print("Screenshot saved to", screenshot_path)
    
    id_token = None
    if "#" in final_url:
        hash_part = final_url.split("#")[1]
        params = {}
        for pair in hash_part.split("&"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                params[k] = v
        id_token = params.get("id_token")
        
    if id_token:
        print("\nSUCCESS: Obtained Google id_token!")
        print("Exchanging Google id_token for Rownd access token...")
        
        rownd_url = "https://api.rownd.io/hub/auth/token"
        rownd_payload = {
            "id_token": id_token,
            "app_id": "b6b8e7c0-fb66-4c6c-a391-bbf0a7d8dfcc"
        }
        r = httpx.post(rownd_url, json=rownd_payload, headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
        print("Rownd Response Status:", r.status_code)
        if r.status_code == 200:
            rownd_data = r.json()
            access_token = rownd_data.get("access_token")
            if access_token:
                print("SUCCESS: Rownd access token obtained!")
                # Call Stardust API
                print("Calling Stardust API...")
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'User-Agent': 'Stardust/5.21.0 (Android; SDK 33)',
                    'Accept': 'application/json'
                }
                stardust_res = httpx.get('https://api.stardust.app/api/v2/my-logs', headers=headers)
                print(f"Stardust API Status: {stardust_res.status_code}")
                if stardust_res.status_code == 200:
                    print("SUCCESS: Fetched Stardust logs!")
                    logs_data = stardust_res.json()
                    
                    # Save to JSON file
                    with open(r"C:\Users\PC\Desktop\nhacuongthuoc\stardust_logs_direct.json", "w", encoding="utf-8") as f_out:
                        json.dump(logs_data, f_out, indent=2, ensure_ascii=False)
                        
                    logs = logs_data if isinstance(logs_data, list) else (logs_data.get('logs', []) or logs_data.get('data', []))
                    period_dates = sorted([log['date'] for log in logs if log.get('period') or log.get('bleeding') or (log.get('flow') and log.get('flow') != 'none')])
                    print(f"\n=== STARDUST PERIOD LOGS (Total days: {len(period_dates)}) ===")
                    if period_dates:
                        from datetime import datetime
                        date_objs = [datetime.strptime(d, "%Y-%m-%d") for d in period_dates]
                        periods = []
                        if date_objs:
                            current_period = [date_objs[0]]
                            for d in date_objs[1:]:
                                if (d - current_period[-1]).days <= 2:
                                    current_period.append(d)
                                else:
                                    periods.append(current_period)
                                    current_period = [d]
                            periods.append(current_period)
                        
                        print("\nRecent period cycles:")
                        for p in periods[-5:]:
                            start_str = p[0].strftime("%d/%m/%Y")
                            end_str = p[-1].strftime("%d/%m/%Y")
                            print(f"  - Từ ngày {start_str} đến ngày {end_str} ({len(p)} ngày)")
                    else:
                        print("No period dates found in the logs.")
                else:
                    print("Stardust API Error:", stardust_res.text)
            else:
                print("Rownd Response did not contain access_token:", r.text)
        else:
            print("Failed to authenticate with Rownd:", r.text)
    else:
        print("\nFAILED: Could not obtain Google id_token.")
        
    browser.close()
