import json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, channel="chrome")
    context = browser.new_context()
    page = context.new_page()
    
    def handle_response(response):
        if "app-config" in response.url:
            print(f"URL: {response.url}")
            print(f"Status: {response.status}")
            print(f"Headers: {response.headers}")
            try:
                text = response.text()
                print(f"Response Body: {text[:2000]}")
            except Exception as e:
                print(f"Could not read body: {e}")
                
    page.on("response", handle_response)
    page.on("console", lambda msg: print(f"Console: {msg.type}: {msg.text}"))
    
    print("Navigating to https://denngay.vercel.app/ ...")
    page.goto("https://denngay.vercel.app/", wait_until="networkidle")
    
    browser.close()
