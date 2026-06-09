import json
import httpx
import urllib.parse

# Configure UTF-8 stdout
import sys
sys.stdout.reconfigure(encoding='utf-8')

cookies_path = r"c:\Users\PC\Desktop\nhacuongthuoc\cookies.txt"

with open(cookies_path, "r", encoding="utf-8") as f:
    raw_cookies = json.load(f)

# Convert to httpx cookies
cookies = {}
for cookie in raw_cookies:
    # Google cookies are typically wildcard on .google.com
    # We only include them if they belong to google.com
    if "google.com" in cookie["domain"]:
        cookies[cookie["name"]] = cookie["value"]

client_id = "900415098360-ritfis4563e74sluvre9nsmhi2oa4uf0.apps.googleusercontent.com"
redirect_uri = "https://denngay.vercel.app"
scope = "openid email profile"
nonce = "stardust_test_12345"
oauth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&redirect_uri={urllib.parse.quote(redirect_uri)}&response_type=id_token&scope={scope.replace(' ', '+')}&nonce={nonce}"

print("Sending direct HTTP GET request to Google OAuth...")
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Upgrade-Insecure-Requests": "1"
}

with httpx.Client(cookies=cookies, headers=headers, follow_redirects=False) as client:
    url = oauth_url
    for i in range(10):
        print(f"\nStep {i}: GET {url}")
        r = client.get(url)
        print(f"Status: {r.status_code}")
        
        # Print location header if redirect
        if r.status_code in [301, 302, 303, 307, 308]:
            location = r.headers.get("Location", "")
            print(f"Redirect Location: {location}")
            
            # If the location points to our redirect_uri, we succeeded!
            if redirect_uri in location:
                print("SUCCESS! Redirected back to denngay.vercel.app!")
                break
                
            # Resolve relative redirect
            if location.startswith("/"):
                # parse base url
                parsed = urllib.parse.urlparse(url)
                url = f"{parsed.scheme}://{parsed.netloc}{location}"
            else:
                url = location
        else:
            print("Response is not a redirect.")
            print(f"Body snippet (first 1000 chars):\n{r.text[:1000]}")
            break
