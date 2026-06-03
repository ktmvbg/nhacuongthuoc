import os
import sys
import urllib.request
import urllib.parse
import urllib.error
import json
import base64
from nacl import encoding, public

# Cấu hình UTF-8 cho console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Đọc cấu hình từ .env
env_file = os.path.join(os.path.dirname(__file__), '.env')
env_vars = {}
if os.path.exists(env_file):
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, val = line.split('=', 1)
                env_vars[key.strip()] = val.strip()

github_token = env_vars.get('GITHUB_TOKEN')
telegram_token = env_vars.get('TELEGRAM_BOT_TOKEN')
telegram_chat_id = env_vars.get('TELEGRAM_CHAT_ID')

if not github_token or not telegram_token or not telegram_chat_id:
    print("Lỗi: Thiếu cấu hình trong file .env (cần GITHUB_TOKEN, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)")
    sys.exit(1)

# Lấy GitHub username
user_req = urllib.request.Request(
    'https://api.github.com/user',
    headers={
        'Authorization': f'Bearer {github_token}',
        'User-Agent': 'Python-Secrets-Setter',
        'Accept': 'application/vnd.github+json'
    }
)
try:
    with urllib.request.urlopen(user_req) as response:
        res = json.loads(response.read().decode('utf-8'))
        username = res['login']
except Exception as e:
    print(f"Lỗi khi lấy thông tin user GitHub: {e}")
    sys.exit(1)

repo_name = "nhacuongthuoc"

# 1. Lấy Public Key của repo để mã hóa Secret
print("Đang lấy Public Key từ GitHub...")
pubkey_url = f"https://api.github.com/repos/{username}/{repo_name}/actions/secrets/public-key"
pubkey_req = urllib.request.Request(
    pubkey_url,
    headers={
        'Authorization': f'Bearer {github_token}',
        'User-Agent': 'Python-Secrets-Setter',
        'Accept': 'application/vnd.github+json'
    }
)

try:
    with urllib.request.urlopen(pubkey_req) as response:
        pubkey_data = json.loads(response.read().decode('utf-8'))
        key_id = pubkey_data['key_id']
        public_key = pubkey_data['key']
        print(f"Lấy Public Key thành công! Key ID: {key_id}")
except urllib.error.HTTPError as e:
    err_body = e.read().decode('utf-8')
    print(f"Lỗi khi lấy Public Key (HTTP {e.code}): {err_body}")
    sys.exit(1)

# Hàm mã hóa secret sử dụng PyNaCl
def encrypt_secret(public_key_b64: str, secret_val: str) -> str:
    public_key = public.PublicKey(public_key_b64.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_val.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")

# 2. Upload các secrets lên GitHub
def set_github_secret(secret_name: str, secret_val: str):
    print(f"Đang mã hóa và đẩy secret '{secret_name}'...")
    encrypted_val = encrypt_secret(public_key, secret_val)
    
    secret_url = f"https://api.github.com/repos/{username}/{repo_name}/actions/secrets/{secret_name}"
    data = json.dumps({
        "encrypted_value": encrypted_val,
        "key_id": key_id
    }).encode('utf-8')
    
    req = urllib.request.Request(
        secret_url,
        data=data,
        headers={
            'Authorization': f'Bearer {github_token}',
            'User-Agent': 'Python-Secrets-Setter',
            'Accept': 'application/vnd.github+json',
            'Content-Type': 'application/json'
        },
        method='PUT'
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status in [201, 204]:
                print(f"Đã cập nhật secret '{secret_name}' thành công!")
            else:
                print(f"Kết quả cập nhật secret '{secret_name}': HTTP {response.status}")
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8')
        print(f"Lỗi khi đẩy secret '{secret_name}' (HTTP {e.code}): {err_body}")
        sys.exit(1)

# Cập nhật hai secrets
set_github_secret("TELEGRAM_BOT_TOKEN", telegram_token)
set_github_secret("TELEGRAM_CHAT_ID", telegram_chat_id)

print("\n=== HOÀN THÀNH CẤU HÌNH SECRETS TỰ ĐỘNG! ===")
print("Bot của bạn đã sẵn sàng chạy trên GitHub Actions.")
