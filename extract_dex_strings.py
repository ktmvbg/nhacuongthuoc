import zipfile
import io
import re

xapk_path = 'c:/Users/PC/Desktop/nhacuongthuoc/Stardust Period Tracker_5.21.0_APKPure.xapk'

z_xapk = zipfile.ZipFile(xapk_path)
apk_data = z_xapk.read('com.stardust.app.apk')
z_apk = zipfile.ZipFile(io.BytesIO(apk_data))

url_pattern = re.compile(b'https?://[a-zA-Z0-9\\.\\-_/\\{\\}\\?\\&\\=\\+\\:]+')
keyword_pattern = re.compile(b'[a-zA-Z0-9\\.\\-_/\\{\\}]{3,}')

stardust_urls = set()
interesting_strings = set()

print("Scanning...")
for f in z_apk.filelist:
    if f.filename.endswith('.dex'):
        data = z_apk.read(f.filename)
        
        for m in url_pattern.findall(data):
            url = m.decode('utf-8', errors='ignore')
            if 'stardust' in url.lower() or 'rownd' in url.lower():
                stardust_urls.add(url)
                
        for m in keyword_pattern.findall(data):
            s = m.decode('utf-8', errors='ignore')
            s_lower = s.lower()
            if any(k in s_lower for k in ['login', 'auth', 'cycle', 'period', 'sync', 'symptom', 'menstruat', 'user/']):
                if len(s) < 80:
                    interesting_strings.add(s)

print("\n=== STARDUST & ROWND URLS ===")
for url in sorted(list(stardust_urls)):
    print(url)

print("\n=== KEYWORDS & ENDPOINTS ===")
for p in sorted(list(interesting_strings)):
    if not (p.startswith('L') and p.endswith(';')):
        print(p)
