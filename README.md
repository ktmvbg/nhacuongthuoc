# 🌸 Bot Telegram Nhắc Uống Thuốc & Website Theo Dõi Sức Khỏe của Quỳnh (100% Serverless & Miễn Phí)

Dự án này đã được tối ưu hóa thành một hệ thống **không máy chủ (Serverless)** hoàn toàn miễn phí 100%, tự động vận hành mà không cần thuê server và không cần cấu hình database ngoài!

*   **Website & Bot Webhook (Vercel):** [https://denngay.vercel.app](https://denngay.vercel.app)
*   **Database (GitHub):** Tự động lưu trữ lịch sử dưới dạng file `db.json` ngay trong repository GitHub riêng tư (Private) của bạn.
*   **Hẹn giờ gửi tin nhắc (GitHub Actions):** Tự động kích hoạt gửi tin nhắn nhắc nhở vào lúc 22:00 hằng ngày hoàn toàn miễn phí.

---

## 🚀 Tính năng nổi bật
1.  **Nút bấm tương tác trên Telegram**: Nhắc Quỳnh uống thuốc kèm nút bấm **Đã uống 🌸** và **Để tí nữa ⏰**.
2.  **Snooze thông minh**: Khi Quỳnh chọn "Để tí nữa", bot sẽ đổi tin nhắn thành hướng dẫn Quỳnh bấm nút uống sau, loại bỏ sự phức tạp của việc hẹn giờ đếm ngược giúp bot hoạt động serverless ổn định.
3.  **Lịch sử & Streak**: Website thống kê chuỗi ngày uống liên tiếp và hiển thị dạng lịch tháng cực dễ thương.
4.  **Gửi tin nhắn kiểm thử**: Tích hợp nút kiểm thử trực tiếp trên website để gửi tin nhắc lập tức nhằm test nút bấm mà không lưu vào lịch sử thật (không ghi vào database).

---

## 🧪 Cách chạy thử nghiệm (Test)
1.  Truy cập vào trang web của bạn: [https://denngay.vercel.app](https://denngay.vercel.app)
2.  Tại thanh bên trái (Sidebar), nhấn nút **Gửi tin nhắc ngay 🚀** (màu tím).
3.  Mở Telegram chat với Bot `@comgioheobot` $\rightarrow$ bạn sẽ nhận được tin nhắn thử nghiệm lập tức!
4.  Bấm thử nút **Đã uống (Test)** hoặc **Để tí nữa (Test)** để xem tin nhắn tự động cập nhật ngay trên màn hình. Lịch sử của lượt bấm này sẽ **không bị ghi vào lịch sử thật** trên database.

---

## 🛠️ Cách cập nhật/Chạy thử local (nếu cần)
Nếu bạn muốn chạy thử code cục bộ dưới máy tính:
1.  Mở file `.env` ở thư mục gốc điền thông tin:
    ```env
    TELEGRAM_BOT_TOKEN=8906408674:AAEsnbLJRseKRtl6i08DE6JDNGvZxwLwKGM
    TELEGRAM_CHAT_ID=1389109644
    GITHUB_TOKEN=your_github_token_here
    ```
2.  Chạy thử script gửi tin nhắn ở local:
    ```powershell
    python send_reminder.py
    ```
