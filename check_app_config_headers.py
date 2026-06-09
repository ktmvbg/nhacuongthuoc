from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, channel="chrome")
    context = browser.new_context()
    page = context.new_page()
    
    def handle_request(request):
        if "app-config" in request.url:
            print(f"\nRequest URL: {request.url}")
            print(f"Headers: {request.headers}")
            
    page.on("request", handle_request)
    
    print("Navigating to https://denngay.vercel.app/ ...")
    page.goto("https://denngay.vercel.app/", wait_until="networkidle")
    
    browser.close()
