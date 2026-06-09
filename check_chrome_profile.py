import os

profile_dir = r"C:\Users\PC\AppData\Local\Google\Chrome\User Data"
print(f"Checking directory: {profile_dir}")

if os.path.exists(profile_dir):
    print("Found Google Chrome User Data directory!")
    # List subdirectories (e.g. Default, Profile 1, etc.)
    subdirs = [d for d in os.listdir(profile_dir) if os.path.isdir(os.path.join(profile_dir, d))]
    print("Available profiles/folders:")
    for d in subdirs[:15]:
        print(f"  {d}")
else:
    print("Chrome User Data directory NOT found at the default path.")
