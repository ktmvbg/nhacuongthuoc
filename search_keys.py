import urllib.request
import re

url = "https://hub.rownd.io/static/scripts/rph.js"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

try:
    with urllib.request.urlopen(req) as res:
        js = res.read().decode('utf-8')
        
        # Look for fqe definition or key prefix
        # We saw fqe(e) and Jn.setItem(fqe(e), s)
        matches = [m.start() for m in re.finditer("fqe=", js)]
        print(f"Found {len(matches)} matches for 'fqe='")
        for m in matches:
            start = max(0, m - 50)
            end = min(len(js), m + 150)
            print(f"fqe= Match: ... {js[start:end]} ...")
            
        # Search for key naming conventions, e.g. "rph_" or "rownd_"
        matches_prefix = [m.start() for m in re.finditer(r'"rph_', js)]
        print(f"Found {len(matches_prefix)} matches for '\"rph_'")
        for m in matches_prefix[:5]:
            start = max(0, m - 50)
            end = min(len(js), m + 150)
            print(f"Prefix Match: ... {js[start:end]} ...")
            
except Exception as e:
    print("Error:", e)
