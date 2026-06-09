import urllib.request
import json

uuids = [
    "b6b8e7c0-fb66-4c6c-a391-bbf0a7d8dfcc",
    "c9705c04-034c-44cc-af28-f76aa267bc5a"
]

for uuid in uuids:
    url = f"https://api.rownd.io/hub/app/{uuid}/config"
    print(f"\nTesting URL: {url}")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = response.read().decode('utf-8')
            config = json.loads(data)
            print(f"Success! Name: {config.get('app', {}).get('name')}, ID: {config.get('app', {}).get('id')}")
    except Exception as e:
        print(f"Failed: {e}")
