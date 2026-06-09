import urllib.request
import re

url = "https://hub.rownd.io/static/scripts/rph.js"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

try:
    with urllib.request.urlopen(req) as res:
        js = res.read().decode('utf-8')
        print(f"Downloaded rph.js, length: {len(js)} characters")
        
        # Search for "app id" or "app_id"
        matches = [m.start() for m in re.finditer("Missing app id", js)]
        print(f"Found {len(matches)} matches for 'Missing app id'")
        for m in matches:
            start = max(0, m - 100)
            end = min(len(js), m + 100)
            print(f"Match context: ... {js[start:end]} ...")
            
        # Search for "Failed to encrypt"
        matches_encrypt = [m.start() for m in re.finditer("Failed to encrypt", js)]
        print(f"Found {len(matches_encrypt)} matches for 'Failed to encrypt'")
        for m in matches_encrypt:
            start = max(0, m - 100)
            end = min(len(js), m + 100)
            print(f"Match context: ... {js[start:end]} ...")
            
except Exception as e:
    print("Error:", e)
