import json

with open("cookies.txt", "r", encoding="utf-8") as f:
    cookies = json.load(f)

domains = {}
for c in cookies:
    domain = c.get("domain", "")
    domains[domain] = domains.get(domain, 0) + 1

print("Cookie domains and counts:")
for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True):
    print(f"  {domain}: {count}")
