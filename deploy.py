import os
import sys
import subprocess
import urllib.request
import urllib.parse
import urllib.error
import json

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
if not github_token:
    print("Lỗi: Không tìm thấy GITHUB_TOKEN trong file .env")
    sys.exit(1)

# 1. Xác thực GitHub Token và lấy Username
print("Đang kiểm tra GitHub Token...")
user_req = urllib.request.Request(
    'https://api.github.com/user',
    headers={
        'Authorization': f'Bearer {github_token}',
        'User-Agent': 'Python-Remind-Bot-Deployer',
        'Accept': 'application/vnd.github+json'
    }
)

username = None
try:
    with urllib.request.urlopen(user_req) as response:
        res = json.loads(response.read().decode('utf-8'))
        username = res['login']
        print(f"Xác thực thành công! Tài khoản GitHub: {username}")
except urllib.error.HTTPError as e:
    err_body = e.read().decode('utf-8')
    print(f"Lỗi xác thực GitHub (HTTP {e.code}): {err_body}")
    print("\nVui lòng kiểm tra lại GITHUB_TOKEN trong file .env xem đã chính xác hoặc hết hạn chưa.")
    sys.exit(1)
except Exception as e:
    print(f"Lỗi kết nối GitHub API: {e}")
    sys.exit(1)

# 2. Tạo Repository mới trên GitHub
repo_name = "nhacuongthuoc"
print(f"Đang tạo repository '{repo_name}' trên GitHub...")
create_repo_data = json.dumps({
    "name": repo_name,
    "private": True,
    "description": "Bot Telegram nhắc nhở uống thuốc hằng ngày"
}).encode('utf-8')

create_req = urllib.request.Request(
    'https://api.github.com/user/repos',
    data=create_repo_data,
    headers={
        'Authorization': f'Bearer {github_token}',
        'User-Agent': 'Python-Remind-Bot-Deployer',
        'Accept': 'application/vnd.github+json',
        'Content-Type': 'application/json'
    },
    method='POST'
)

repo_created = False
try:
    with urllib.request.urlopen(create_req) as response:
        res = json.loads(response.read().decode('utf-8'))
        print(f"Tạo repository thành công: {res['html_url']}")
        repo_created = True
except urllib.error.HTTPError as e:
    err_body = e.read().decode('utf-8')
    err_json = json.loads(err_body)
    # Nếu repository đã tồn tại
    if e.code == 422 and any(err.get('message') == 'name already exists on this account' for err in err_json.get('errors', [])):
        print(f"Repository '{repo_name}' đã tồn tại trên tài khoản của bạn. Tiến hành đẩy code lên repo hiện tại.")
        repo_created = True
    else:
        print(f"Lỗi khi tạo repository (HTTP {e.code}): {err_body}")
        sys.exit(1)

# 3. Khởi tạo Git cục bộ và Push
if repo_created:
    print("\nBắt đầu cấu hình Git và đẩy code lên...")
    
    def run_cmd(args, check=True):
        res = subprocess.run(args, capture_output=True, text=True, encoding='utf-8')
        if check and res.returncode != 0:
            print(f"Lỗi khi chạy lệnh {' '.join(args)}:")
            print(res.stderr)
            sys.exit(1)
        return res

    # Khởi tạo git nếu chưa có
    if not os.path.exists('.git'):
        run_cmd(['git', 'init'])
        print("- Đã khởi tạo Git repository cục bộ.")

    # Cấu hình git user name/email tạm thời nếu chưa được thiết lập hệ thống
    name_check = subprocess.run(['git', 'config', 'user.name'], capture_output=True, text=True)
    if not name_check.stdout.strip():
        run_cmd(['git', 'config', 'user.name', username])
        run_cmd(['git', 'config', 'user.email', f"{username}@users.noreply.github.com"])
        print("- Đã cấu hình git user tạm thời.")

    # Add và commit
    run_cmd(['git', 'add', '.'])
    # Commit nếu có thay đổi
    status = run_cmd(['git', 'status', '--porcelain'])
    if status.stdout.strip():
        run_cmd(['git', 'commit', '-m', 'Initial commit - Telegram Reminder Bot'])
        print("- Đã tạo commit mới.")
    else:
        print("- Không có thay đổi mới để commit.")

    # Tạo branch main
    run_cmd(['git', 'branch', '-M', 'main'])

    # Cấu hình remote URL chứa token
    remote_url = f"https://x-access-token:{github_token}@github.com/{username}/{repo_name}.git"
    
    # Kiểm tra xem remote origin đã tồn tại chưa
    remote_check = subprocess.run(['git', 'remote', 'get-url', 'origin'], capture_output=True, text=True)
    if remote_check.returncode == 0:
        run_cmd(['git', 'remote', 'set-url', 'origin', remote_url])
    else:
        run_cmd(['git', 'remote', 'add', 'origin', remote_url])
    print("- Đã liên kết với repository từ xa.")

    # Push lên GitHub
    print("Đang đẩy code lên GitHub...")
    run_cmd(['git', 'push', '-u', 'origin', 'main', '--force'])
    print("\n=== ĐÃ HOÀN THÀNH ĐẨY CODE LÊN GITHUB ACTIONS! ===")
    print(f"Địa chỉ repository: https://github.com/{username}/{repo_name}")
    print("\nBước tiếp theo để Bot hoạt động:")
    print(f"1. Truy cập: https://github.com/{username}/{repo_name}/settings/secrets/actions")
    print("2. Thêm hai Repository Secret sau:")
    print("   - Name: TELEGRAM_BOT_TOKEN | Value: <Token Telegram của bạn>")
    print("   - Name: TELEGRAM_CHAT_ID   | Value: 1389109644 (ID của Quỳnh)")
    print("\nSau khi thêm xong, bot sẽ tự chạy lúc 22:00 hằng ngày.")
    print("Bạn có thể sang tab 'Actions' trên repo để ấn chạy thử (Run workflow) bất cứ lúc nào!")
