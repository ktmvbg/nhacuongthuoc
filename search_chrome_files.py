import os
import re
import shutil
import json

src_dir = r"C:\Users\PC\AppData\Local\Google\Chrome\User Data\Profile 1"
temp_dir = r"c:\Users\PC\Desktop\nhacuongthuoc\temp_chrome_search"

if not os.path.exists(src_dir):
    print(f"Profile folder not found: {src_dir}")
    exit(1)

print(f"Scanning Chrome Profile 1: {src_dir}")

jwt_pattern = re.compile(r'\beyJ[A-Za-z0-9-_]+\.eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_=]+\b')
found_tokens = set()

# We will look in local storage, session storage, indexeddb, databases, etc.
dirs_to_search = ["Local Storage", "Session Storage", "IndexedDB", "Databases"]

for folder in dirs_to_search:
    folder_path = os.path.join(src_dir, folder)
    if os.path.exists(folder_path):
        print(f"Searching in folder: {folder}")
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    if os.path.getsize(filepath) > 10 * 1024 * 1024: # Skip files > 10MB
                        continue
                    # Read binary
                    with open(filepath, "rb") as f:
                        data = f.read()
                        text = data.decode("ascii", errors="ignore")
                        matches = jwt_pattern.findall(text)
                        for m in matches:
                            found_tokens.add(m)
                except Exception as e:
                    pass

print(f"Found {len(found_tokens)} unique JWT tokens in Chrome Profile:")
for token in found_tokens:
    print(f"\nToken (length: {len(token)}):")
    print(f"  {token[:50]}...")
    try:
        import base64
        payload_part = token.split(".")[1]
        padded = payload_part + "=" * (4 - len(payload_part) % 4)
        payload = base64.b64decode(padded).decode("utf-8", errors="ignore")
        payload_data = json.loads(payload)
        print("  Decoded Payload:")
        print(json.dumps(payload_data, indent=2))
        
        # Save Rownd token
        if "rownd.io" in str(payload_data) or "337080849221550671" in str(payload_data):
            token_path = r"C:\Users\PC\Desktop\nhacuongthuoc\rownd_token_extracted.txt"
            with open(token_path, "w") as tf:
                tf.write(token)
            print(f"  Saved Stardust Rownd token to {token_path}")
    except Exception as e:
        print(f"  Failed to decode: {e}")
