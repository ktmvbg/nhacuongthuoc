import os

desktop_dir = r"c:\Users\PC\Desktop"
print(f"Scanning Desktop for cookie files...")

for root, dirs, files in os.walk(desktop_dir):
    if '.git' in root or 'node_modules' in root or 'AppData' in root:
        continue
    for file in files:
        if 'cookie' in file.lower():
            filepath = os.path.join(root, file)
            print(f"Found cookie file: {filepath} ({os.path.getsize(filepath)} bytes)")
