import json

with open("cookies.txt", "r", encoding="utf-8") as f:
    cookies = json.load(f)

print(f"Total cookies: {len(cookies)}")
domains = {}
for c in cookies:
    domain = c.get("domain", "")
    domains[domain] = domains.get(domain, 0) + 1

for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True):
    print(f"  {domain}: {count}")

print("\nDetail of some key cookies:")
for c in cookies:
    name = c.get("name", "")
    domain = c.get("domain", "")
    if "SID" in name or "HSID" in name or "SSID" in name or "APISID" in name or "SAPISID" in name or "GAPS" in name:
        print(f"  Domain: {domain} | Name: {name} | Value length: {len(c.get('value', ''))} | Secure: {c.get('secure')} | HttpOnly: {c.get('httpOnly')}")
