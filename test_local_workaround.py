import json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, channel="chrome")
    context = browser.new_context()
    
    # Set localStorage for the domain before page loads
    page = context.new_page()
    
    # We first navigate to the site to set up the origin context,
    # then write to localStorage, then reload.
    print("Navigating to site first...")
    page.goto("https://denngay.vercel.app/", wait_until="commit")
    
    print("Setting pre-populated localStorage rph_state...")
    page.evaluate("() => localStorage.setItem('rph_state', JSON.stringify({ app: { id: '337080849221550671' } }))")
    
    # Now listen to console messages
    errors = []
    def handle_console(msg):
        print(f"Console: {msg.type}: {msg.text}")
        if msg.type == "error":
            errors.append(msg.text)
            
    page.on("console", handle_console)
    page.on("pageerror", lambda err: print(f"PageError: {err}"))
    
    print("Reloading page with pre-populated state...")
    page.goto("https://denngay.vercel.app/", wait_until="networkidle")
    
    if any("Missing app id" in err for err in errors):
        print("\nWorkaround FAILED: Missing app id error still occurred.")
    else:
        print("\nWorkaround SUCCESS! No Missing app id error occurred.")
        
    browser.close()
