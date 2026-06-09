import os
import re
import shutil

# Configure UTF-8 stdout
import sys
sys.stdout.reconfigure(encoding='utf-8')

src_dir = r"C:\Users\PC\AppData\Local\Google\Chrome\User Data\Profile 1\Local Storage\leveldb"
temp_dir = r"c:\Users\PC\Desktop\nhacuongthuoc\temp_leveldb"

if not os.path.exists(src_dir):
    print(f"LevelDB folder not found at: {src_dir}")
    exit(1)

print(f"Scanning LevelDB directory: {src_dir}")

# Clean and copy to avoid locking issues
if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)
os.makedirs(temp_dir, exist_ok=True)

for file in os.listdir(src_dir):
    src_file = os.path.join(src_dir, file)
    dest_file = os.path.join(temp_dir, file)
    if os.path.isfile(src_file):
        try:
            shutil.copy2(src_file, dest_file)
        except Exception as e:
            print(f"Could not copy {file}: {e}")

jwt_pattern = re.compile(r'\beyJ[A-Za-z0-9-_]+\.eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_=]+\b')
found_tokens = set()

for file in os.listdir(temp_dir):
    filepath = os.path.join(temp_dir, file)
    if os.path.isfile(filepath):
        try:
            with open(filepath, "rb") as f:
                data = f.read()
                # Decode as ASCII, ignoring errors
                text = data.decode("ascii", errors="ignore")
                matches = jwt_pattern.findall(text)
                for m in matches:
                    found_tokens.add(m)
        except Exception as e:
            print(f"Error reading {file}: {e}")

print(f"Found {len(found_tokens)} unique JWT tokens:")
for token in found_tokens:
    print(f"\nToken (length: {len(token)}):")
    print(f"  {token[:50]}...")
    # Decode token payload to inspect it
    try:
        import base64
        payload_part = token.split(".")[1]
        # Pad payload_part to be multiple of 4
        padded = payload_part + "=" * (4 - len(payload_part) % 4)
        payload = base64.b64decode(padded).decode("utf-8", errors="ignore")
        payload_data = json.loads(payload)
        print("  Decoded Payload:")
        print(json.dumps(payload_data, indent=2))
        
        # Save token if it's the Rownd access token
        # Rownd tokens usually have app_id or aud pointing to rownd or stardust
        if "rownd.io" in str(payload_data) or "337080849221550671" in str(payload_data):
            token_path = r"C:\Users\PC\Desktop\nhacuongthuoc\rownd_token_extracted.txt"
            with open(token_path, "w") as tf:
                tf.write(token)
            print(f"  Saved Stardust Rownd token to {token_path}")
            
    except Exception as e:
        print(f"  Failed to decode payload: {e}")

# Clean up temp files
shutil.rmtree(temp_dir)
print("Finished scan.")
