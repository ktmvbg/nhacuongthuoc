import os

user_data_dir = r"C:\Users\PC\AppData\Local\Google\Chrome\User Data"
if os.path.exists(user_data_dir):
    items = os.listdir(user_data_dir)
    print("Found Chrome User Data directory. Searching for profile folders:")
    for item in items:
        item_path = os.path.join(user_data_dir, item)
        if os.path.isdir(item_path):
            # Check if there is a 'Preferences' file in this folder (which indicates a Chrome Profile)
            pref_path = os.path.join(item_path, 'Preferences')
            if os.path.exists(pref_path):
                print(f"  Profile Folder: {item}")
else:
    print("Chrome User Data directory does not exist.")
