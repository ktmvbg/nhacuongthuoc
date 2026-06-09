import urllib.request

paths = [
    "https://stardust.rownd.link/static/scripts/rph.js",
    "https://stardust.rownd.link/hub/app-config"
]

for url in paths:
    print(f"Testing: {url}")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as res:
            print(f"  Success: {res.status} (length: {len(res.read())})")
    except Exception as e:
        print(f"  Failed: {e}")
