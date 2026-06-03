import os
import sys
import json
import urllib.request
import urllib.parse

# Cấu hình UTF-8 cho console để tránh lỗi hiển thị tiếng Việt trên Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Đọc db.json để kiểm tra xem Quỳnh đã uống thuốc chưa
db_path = os.path.join(os.path.dirname(__file__), 'db.json')

if os.path.exists(db_path):
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            logs = json.load(f)
            if logs:
                # Lấy bản ghi cuối cùng trong cơ sở dữ liệu
                latest_log = logs[-1]
                if latest_log.get('status') == 'taken':
                    print("Quỳnh đã uống thuốc rồi. Không cần nhắc lại!")
                    sys.exit(0)
    except Exception as e:
        print(f"Lỗi khi đọc file db.json: {e}")
else:
    print("Không tìm thấy file db.json. Tiến hành gửi tin nhắc nhở.")

# Lấy cấu hình từ môi trường (do GitHub Action truyền vào)
token = os.environ.get('TELEGRAM_BOT_TOKEN')
chat_id = os.environ.get('TELEGRAM_CHAT_ID')

if not token or not chat_id:
    print("Lỗi: Thiếu biến môi trường TELEGRAM_BOT_TOKEN hoặc TELEGRAM_CHAT_ID.")
    sys.exit(1)

# Giao diện nút bấm nhắc nhở lại
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
    print(f"Đã xảy ra lỗi: {e}")
    sys.exit(1)
