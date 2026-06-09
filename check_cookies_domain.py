import json
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
    browser = p.chromium.launch(headless=True, channel="chrome")
    context = browser.new_context()
    context.add_cookies(playwright_cookies)
    
    print("Cookies for https://contacts.google.com:")
    for c in context.cookies("https://contacts.google.com"):
        print(f"  {c['name']} (domain: {c['domain']})")
        
    print("\nCookies for https://accounts.google.com:")
    for c in context.cookies("https://accounts.google.com"):
        print(f"  {c['name']} (domain: {c['domain']})")
        
    browser.close()
