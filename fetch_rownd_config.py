import urllib.request
import json

app_key = "b6b8e7c0-fb66-4c6c-a391-bbf0a7d8dfcc"
url = "https://api.rownd.io/hub/app-config"

req = urllib.request.Request(url)
req.add_header('x-rownd-app-key', app_key)
req.add_header('User-Agent', 'Mozilla/5.0')

try:
    with urllib.request.urlopen(req) as response:
        data = response.read().decode('utf-8')
        config = json.loads(data)
        print("Rownd Configuration:")
        print(json.dumps(config, indent=2))
except Exception as e:
    print(f"Error fetching Rownd config: {e}")
