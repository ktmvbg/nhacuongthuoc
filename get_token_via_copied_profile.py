import os
import shutil
import sys
import time
import json
import urllib.parse
import httpx
from playwright.sync_api import sync_playwright

# Configure UTF-8 stdout
sys.stdout.reconfigure(encoding='utf-8')

src_dir = r"C:\Users\PC\AppData\Local\Google\Chrome\User Data"
dest_dir = r"c:\Users\PC\Desktop\nhacuongthuoc\temp_profile"

# Clean dest_dir
if os.path.exists(dest_dir):
    try:
        shutil.rmtree(dest_dir)
    except Exception as e:
        print(f"Warning: could not clean dest_dir: {e}")

os.makedirs(os.path.join(dest_dir, "Default", "Network"), exist_ok=True)

# Copy Local State
local_state_src = os.path.join(src_dir, "Local State")
local_state_dest = os.path.join(dest_dir, "Local State")
if os.path.exists(local_state_src):
    try:
        shutil.copy2(local_state_src, local_state_dest)
        print("Copied Local State.")
    except Exception as e:
        print(f"Warning copying Local State: {e}")

# Copy Preferences from Profile 1
pref_src = os.path.join(src_dir, "Profile 1", "Preferences")
pref_dest = os.path.join(dest_dir, "Default", "Preferences")
if os.path.exists(pref_src):
    try:
        shutil.copy2(pref_src, pref_dest)
        print("Copied Preferences from Profile 1.")
    except Exception as e:
        print(f"Warning copying Preferences: {e}")

# Copy Cookies from Profile 1
cookies_src = os.path.join(src_dir, "Profile 1", "Network", "Cookies")
cookies_dest = os.path.join(dest_dir, "Default", "Network", "Cookies")
if os.path.exists(cookies_src):
    try:
        shutil.copy2(cookies_src, cookies_dest)
        print("Copied Cookies database from Profile 1.")
    except Exception as e:
        print(f"Error copying Cookies database: {e}")
        sys.exit(1)

# Custom Google OAuth parameters using the user's client ID
client_id = "900415098360-ritfis4563e74sluvre9nsmhi2oa4uf0.apps.googleusercontent.com"
redirect_uri = "https://denngay.vercel.app"
scope = "openid email profile"
nonce = "stardust_test_12345"
oauth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&redirect_uri={urllib.parse.quote(redirect_uri)}&response_type=id_token&scope={scope.replace(' ', '+')}&nonce={nonce}"

with sync_playwright() as p:
    print("Launching chrome with cloned persistent context...")
    context = p.chromium.launch_persistent_context(
        user_data_dir=dest_dir,
        headless=True,
        channel="chrome",
        viewport={"width": 1280, "height": 720}
    )
    
    page = context.new_page()
    
    print("Pre-warming Google session on Contacts...")
    page.goto("https://contacts.google.com/", wait_until="load")
    time.sleep(3)
    print("Contacts Page Title:", page.title())
    
    # Take screenshot of contacts to verify we are logged in
    page.screenshot(path=r"C:\Users\PC\Desktop\nhacuongthuoc\contacts_profile1.png")
    
    print("Navigating to Google OAuth URL...")
    page.goto(oauth_url, wait_until="load")
    time.sleep(5)
    
    final_url = page.url
    print("Final URL:", final_url)
    print("Page Title:", page.title())
    
    # Save a screenshot to help debug
    page.screenshot(path=r"C:\Users\PC\Desktop\nhacuongthuoc\oauth_profile1_final.png")
    
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
                    
                    # Sort and extract period logs
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
        
    context.close()
