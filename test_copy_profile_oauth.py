import os
import shutil
import sys
import time
import json
from playwright.sync_api import sync_playwright

src_dir = r"C:\Users\PC\AppData\Local\Google\Chrome\User Data"
dest_dir = r"c:\Users\PC\Desktop\nhacuongthuoc\temp_profile"

# Ensure clean destination directory
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
    shutil.copy2(local_state_src, local_state_dest)
    print("Copied Local State.")

# Copy Preferences
pref_src = os.path.join(src_dir, "Default", "Preferences")
pref_dest = os.path.join(dest_dir, "Default", "Preferences")
if os.path.exists(pref_src):
    shutil.copy2(pref_src, pref_dest)
    print("Copied Preferences.")

# Copy Cookies
cookies_src = os.path.join(src_dir, "Default", "Network", "Cookies")
cookies_dest = os.path.join(dest_dir, "Default", "Network", "Cookies")
if os.path.exists(cookies_src):
    # If Chrome is running, the Cookies file might be locked.
    # We can try to copy it, or ignore lock by using shutil
    try:
        shutil.copy2(cookies_src, cookies_dest)
        print("Copied Cookies database.")
    except Exception as e:
        print(f"Error copying Cookies database: {e}")
        sys.exit(1)

with sync_playwright() as p:
    print("Launching chrome with cloned persistent context...")
    # Launch persistent context using system chrome channel
    context = p.chromium.launch_persistent_context(
        user_data_dir=dest_dir,
        headless=True,
        channel="chrome",
        viewport={"width": 1280, "height": 720}
    )
    
    page = context.new_page()
    
    tokens_captured = []
    
    def handle_request(req):
        if "rownd.io" in req.url:
            print(f"[Rownd Request] {req.method} {req.url}")
                
    def handle_response(res):
        if "rownd.io" in res.url:
            print(f"[Rownd Response] {res.status} {res.url}")
            try:
                content_type = res.headers.get("content-type", "")
                if "application/json" in content_type:
                    text = res.text()
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
    print("Contacts Page Title:", page.title().encode('ascii', 'ignore').decode('ascii'))
    
    oauth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        "client_id=442565757208-2fk8nhdbnk679hkqvmtthsvt1p4bbpmu.apps.googleusercontent.com&"
        "redirect_uri=https%3A%2F%2Fapi.rownd.io%2Fhub%2Fauth%2Fgoogle%2Fcallback&"
        "response_type=code&"
        "scope=openid+email+profile&"
        "state=12345&"
        "login_hint=rbkya2013@gmail.com"
    )
    
    print("\n--- Navigating to Google OAuth URL ---")
    page.goto(oauth_url, wait_until="load")
    time.sleep(5)
    
    print("\nFinal URL:", page.url)
    print("Page Title:", page.title().encode('ascii', 'ignore').decode('ascii'))
    
    page.screenshot(path="C:\\Users\\PC\\.gemini\\antigravity-ide\\brain\\98487492-efcc-4a4a-9527-94f16c05be12\\oauth_persistent.png")
    
    if tokens_captured:
        print(f"Successfully captured {len(tokens_captured)} token(s)!")
        token_path = r"C:\Users\PC\.gemini\antigravity-ide\brain\98487492-efcc-4a4a-9527-94f16c05be12\scratch\rownd_token.txt"
        with open(token_path, "w") as f:
            f.write(tokens_captured[0])
        print(f"Saved token to {token_path}")
    else:
        print("No tokens captured.")
        
    context.close()
