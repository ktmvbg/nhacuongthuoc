import zipfile
import io
import re

xapk_path = 'c:/Users/PC/Desktop/nhacuongthuoc/Stardust Period Tracker_5.21.0_APKPure.xapk'

z_xapk = zipfile.ZipFile(xapk_path)
apk_data = z_xapk.read('com.stardust.app.apk')
z_apk = zipfile.ZipFile(io.BytesIO(apk_data))

# Biểu thức tìm chuỗi ASCII/UTF-8 dài từ 4 ký tự trở lên
string_pattern = re.compile(b'[a-zA-Z0-9\\.\\-_/\\{\\}\\?\\&\\=\\+\\:]{4,}')

print("Scanning DEX files for endpoints and auth...")

stardust_endpoints = set()
rownd_endpoints = set()
google_auth_terms = set()
all_urls = set()

for f in z_apk.filelist:
    if f.filename.endswith('.dex'):
        data = z_apk.read(f.filename)
        matches = string_pattern.findall(data)
        
        for m in matches:
            try:
                s = m.decode('ascii').strip()
            except:
                continue
                
            s_lower = s.lower()
            
            # Phân loại các chuỗi tìm thấy
            if 'stardust' in s_lower:
                if s.startswith('/') or 'api' in s_lower or 'v1' in s_lower:
                    stardust_endpoints.add(s)
            elif 'rownd.io' in s_lower:
                rownd_endpoints.add(s)
            elif 'google' in s_lower and ('login' in s_lower or 'sign' in s_lower or 'auth' in s_lower or 'token' in s_lower or 'credential' in s_lower):
                google_auth_terms.add(s)
            elif s.startswith('http://') or s.startswith('https://'):
                if 'stardust' in s_lower or 'rownd' in s_lower:
                    all_urls.add(s)

print("\n=== BASE URLS ===")
for url in sorted(list(all_urls)):
    print(url)

print("\n=== DETECTED ENDPOINTS ===")
endpoints = [s for s in stardust_endpoints if s.startswith('/') or 'api' in s.lower()]
for ep in sorted(endpoints)[:60]:
    print(ep)

print("\n=== ROWND AUTH REFERENCES ===")
for ep in sorted(list(rownd_endpoints)):
    print(ep)

print("\n=== GOOGLE AUTH KEYWORDS ===")
for term in sorted(list(google_auth_terms))[:30]:
    print(term)
