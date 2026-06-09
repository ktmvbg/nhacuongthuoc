import urllib.request

subdomains = [
    "https://stardust.rownd.link",
    "https://stardust.hub.rownd.io",
    "https://hub.rownd.io"
]

for url in subdomains:
    print(f"Testing: {url}")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as res:
            print(f"  Success: {res.status} (URL: {res.url})")
    except Exception as e:
        print(f"  Failed: {e}")
