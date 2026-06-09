import urllib.request
import re

url = "https://hub.rownd.io/static/scripts/rph.js"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

try:
    with urllib.request.urlopen(req) as res:
        js = res.read().decode('utf-8')
        
        matches = [m.start() for m in re.finditer(r"\buS\s*=\s*", js)]
        print(f"Found {len(matches)} matches for 'uS='")
        for m in matches:
            start = max(0, m - 50)
            end = min(len(js), m + 150)
            print(f"Match: ... {js[start:end]} ...")
            
        matches_arrow = [m.start() for m in re.finditer(r"\buS\s*=\s*\(", js)]
        print(f"Found {len(matches_arrow)} matches for 'uS=('")
        for m in matches_arrow:
            start = max(0, m - 50)
            end = min(len(js), m + 150)
            print(f"Match: ... {js[start:end]} ...")
            
except Exception as e:
    print("Error:", e)
