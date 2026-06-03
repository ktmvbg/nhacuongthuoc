import os
import sys
import json
import time
import urllib.request
import urllib.parse
import base64
from datetime import datetime

# Cấu hình UTF-8 cho console để tránh lỗi hiển thị tiếng Việt trên Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

owner = "ktmvbg"
repo = "nhacuongthuoc"

def get_db_logs():
    token = os.environ.get('GITHUB_TOKEN')
    db_path = os.path.join(os.path.dirname(__file__), 'db.json')
    
    if token:
        # Fetch trực tiếp từ GitHub API để lấy dữ liệu mới nhất
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/db.json"
        req = urllib.request.Request(
            url,
            headers={
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'GitHub-Actions'
            }
        )
        try:
            with urllib.request.urlopen(req) as res:
                data = json.loads(res.read().decode('utf-8'))
                decoded = base64.b64decode(data['content']).decode('utf-8')
                return json.loads(decoded), data['sha']
        except Exception as e:
            print(f"Lỗi gọi GitHub API, dùng file local làm fallback: {e}")
            
    if os.path.exists(db_path):
        with open(db_path, 'r', encoding='utf-8') as f:
            return json.load(f), None
    return [], None

print("=== BẮT ĐẦU TIẾN TRÌNH SNOOZE ===")

# 1. Đọc db.json lúc bắt đầu chạy
logs, _ = get_db_logs()
if not logs:
    print("Database rỗng hoặc không tồn tại. Kết thúc.")
    sys.exit(0)

latest_log = logs[-1]
status = latest_log.get('status')
created_at_str = latest_log.get('created_at')

print(f"Trạng thái hiện tại trong DB: {status} (Thời gian tạo: {created_at_str})")

if status == 'taken':
    print("Quỳnh đã uống thuốc rồi. Không cần nhắc nhở nữa!")
    sys.exit(0)

if status != 'delayed':
    print(f"Trạng thái cuối là '{status}', không phải 'delayed'. Kết thúc tiến trình.")
    sys.exit(0)

# 2. Tính thời gian cần ngủ
try:
    if created_at_str.endswith('Z'):
        dt_str = created_at_str[:-1]
    else:
        dt_str = created_at_str
    created_dt = datetime.fromisoformat(dt_str)
    
    # Lấy giờ UTC hiện tại
    now_utc = datetime.utcnow()
    
    time_passed = (now_utc - created_dt).total_seconds()
    sleep_time = 600 - time_passed # 10 phút = 600 giây
    
    if sleep_time > 0:
        print(f"Đã trôi qua {time_passed:.1f} giây kể từ khi click 'Để tí nữa'.")
        print(f"Sẽ ngủ trong {sleep_time:.1f} giây để đủ 10 phút...")
        time.sleep(sleep_time)
    else:
        print(f"Đã quá 10 phút kể từ lúc click ({time_passed:.1f} giây). Sẽ chạy tiếp không ngủ.")
except Exception as e:
    print(f"Lỗi tính toán thời gian, ngủ mặc định 10 phút: {e}")
    time.sleep(600)

print("\n--- ĐÃ HẾT GIỜ HẸN GIỜ, TIẾN HÀNH KIỂM TRA LẠI DATABASE ---")

# 3. Sau khi ngủ xong, tải lại db.json mới nhất từ GitHub API để kiểm tra xem trong lúc ngủ Quỳnh đã bấm gì khác chưa
logs_after, _ = get_db_logs()
if not logs_after:
    print("Lỗi: Không lấy được dữ liệu sau khi ngủ.")
    sys.exit(1)

latest_log_after = logs_after[-1]
status_after = latest_log_after.get('status')
created_at_after_str = latest_log_after.get('created_at')

print(f"Trạng thái sau khi ngủ: {status_after} (Thời gian tạo: {created_at_after_str})")

# Nếu trạng thái đã đổi thành 'taken'
if status_after == 'taken':
    print("Trong lúc chờ, Quỳnh đã bấm 'Đã uống'. Huỷ nhắc nhở này.")
    sys.exit(0)

# Nếu timestamp của bản ghi cuối đã thay đổi (nghĩa là có một click 'Để tí nữa' mới hơn)
if created_at_after_str != created_at_str:
    print(f"Đã có một yêu cầu hẹn nhắc mới hơn ({created_at_after_str} so với {created_at_str}). Yêu cầu này sẽ do tiến trình mới xử lý. Huỷ nhắc nhở ở tiến trình hiện tại để tránh tin nhắn trùng lặp.")
    sys.exit(0)

# 4. Nếu trạng thái vẫn là 'delayed' và trùng khớp timestamp cũ, tiến hành gửi tin nhắn nhắc nhở
token = os.environ.get('TELEGRAM_BOT_TOKEN')
chat_id = os.environ.get('TELEGRAM_CHAT_ID')

if not token or not chat_id:
    print("Lỗi: Thiếu TELEGRAM_BOT_TOKEN hoặc TELEGRAM_CHAT_ID.")
    sys.exit(1)

reply_markup = {
    "inline_keyboard": [
        [
            {"text": "Đã uống 🌸", "callback_data": "taken"},
            {"text": "Để tí nữa ⏰", "callback_data": "later"}
        ]
    ]
}

url = f"https://api.telegram.org/bot{token}/sendMessage"
data = urllib.parse.urlencode({
    'chat_id': chat_id,
    'text': "Quỳnh ơi, đã 10 phút trôi qua rồi, nhớ uống thuốc nhé em iu! 🌸",
    'reply_markup': json.dumps(reply_markup)
}).encode('utf-8')

req = urllib.request.Request(url, data=data, method='POST')
req.add_header('Content-Type', 'application/x-www-form-urlencoded')

try:
    print("Đang gửi tin nhắc nhở lại (snooze)...")
    with urllib.request.urlopen(req) as response:
        res_body = response.read().decode('utf-8')
        res_json = json.loads(res_body)
        if res_json.get("ok"):
            print("Tin nhắn nhắc nhở lại đã được gửi thành công!")
        else:
            print(f"Gửi tin nhắn thất bại: {res_body}")
            sys.exit(1)
except Exception as e:
    print(f"Lỗi gửi tin nhắn: {e}")
    sys.exit(1)
