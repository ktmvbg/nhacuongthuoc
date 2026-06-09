import os
import re

brain_dir = r"C:\Users\PC\.gemini\antigravity-ide\brain"
jwt_pattern = re.compile(r'\beyJ[A-Za-z0-9-_]+\.eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_=]+\b')

print("Scanning brain folders for JWT tokens...")
found = False

if os.path.exists(brain_dir):
    for root, dirs, files in os.walk(brain_dir):
        # Skip some media or temp dirs if any
        if '.tempmediaStorage' in root or 'browser_recordings' in root:
            continue
        for file in files:
            if file.endswith(('.txt', '.json', '.log', '.md', '.js', '.py')):
                filepath = os.path.join(root, file)
                try:
                    # Avoid reading huge binary files
                    if os.path.getsize(filepath) > 2 * 1024 * 1024:
                        continue
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        matches = jwt_pattern.findall(content)
                        if matches:
                            print(f"\nFound token in file: {filepath}")
                            for match in set(matches):
                                # Print first 30 chars and length
                                print(f"  Token: {match[:40]}... (length: {len(match)})")
                            found = True
                except Exception as e:
                    pass
else:
    print(f"Directory not found: {brain_dir}")

if not found:
    print("No JWT tokens found in any brain directory.")
