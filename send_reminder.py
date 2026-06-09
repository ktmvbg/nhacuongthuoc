import sys
import os
import urllib.request
import urllib.parse
import urllib.error
import json

# Cấu hình UTF-8 cho console để tránh lỗi hiển thị tiếng Việt trên Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Tải cấu hình từ file .env nếu có (khi chạy thử local)
env_file = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_file):
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, val = line.split('=', 1)
                os.environ[key.strip()] = val.strip()

token = os.environ.get('TELEGRAM_BOT_TOKEN')
chat_id = os.environ.get('TELEGRAM_CHAT_ID')

if not token or not chat_id:
    print("Lỗi: Thiếu biến môi trường TELEGRAM_BOT_TOKEN hoặc TELEGRAM_CHAT_ID.")
    exit(1)

# Định nghĩa giao diện nút bấm tương tác
reply_markup = {
    "inline_keyboard": [
        [
            {"text": "Đã uống 🌸", "callback_data": "taken"},
            {"text": "Để tí nữa ⏰", "callback_data": "later"},
            {"text": "Nay em nghỉ 💤", "callback_data": "off"}
        ]
    ]
}

url = f"https://api.telegram.org/bot{token}/sendMessage"
data = urllib.parse.urlencode({
    'chat_id': chat_id,
    'text': "Đến giờ uống thuốc rồi em iu ơi! 🌸",
    'reply_markup': json.dumps(reply_markup)
}).encode('utf-8')

req = urllib.request.Request(url, data=data, method='POST')
req.add_header('Content-Type', 'application/x-www-form-urlencoded')

try:
    print("Đang gửi tin nhắc nhở kèm nút bấm tương tác...")
    with urllib.request.urlopen(req) as response:
        res_body = response.read().decode('utf-8')
        res_json = json.loads(res_body)
        if res_json.get("ok"):
            print("Tin nhắn nhắc nhở đã được gửi thành công!")
        else:
            print(f"Gửi tin nhắn thất bại: {res_body}")
except urllib.error.HTTPError as he:
    err_body = he.read().decode('utf-8')
    print(f"Đã xảy ra lỗi HTTP {he.code}: {err_body}")
    exit(1)
except Exception as e:
    print(f"Đã xảy ra lỗi hệ thống: {e}")
    exit(1)
