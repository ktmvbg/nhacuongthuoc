import os
import re

workspace_dir = r"c:\Users\PC\Desktop\nhacuongthuoc"
jwt_pattern = re.compile(r'\beyJ[A-Za-z0-9-_]+\.eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_=]+\b')

print("Scanning workspace folders for JWT tokens...")
found = False

for root, dirs, files in os.walk(workspace_dir):
    if '.git' in root or 'node_modules' in root:
        continue
    for file in files:
        if file.endswith(('.txt', '.json', '.log', '.md', '.js', '.py')):
            filepath = os.path.join(root, file)
            try:
                if os.path.getsize(filepath) > 5 * 1024 * 1024:
                    continue
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    matches = jwt_pattern.findall(content)
                    if matches:
                        print(f"\nFound token in file: {filepath}")
                        for match in set(matches):
                            print(f"  Token: {match[:45]}... (length: {len(match)})")
                        found = True
            except Exception as e:
                pass

if not found:
    print("No JWT tokens found in workspace.")
