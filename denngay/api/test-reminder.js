export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const botToken = process.env.TELEGRAM_BOT_TOKEN;
  const chatId = process.env.TELEGRAM_CHAT_ID;

  if (!botToken || !chatId) {
    return res.status(500).json({ error: 'Thiếu cấu hình Telegram Token hoặc Chat ID' });
  }

  const replyMarkup = {
    inline_keyboard: [
      [
        { text: 'Đã uống 🌸 (Test)', callback_data: 'test_taken' },
        { text: 'Để tí nữa ⏰ (Test)', callback_data: 'test_later' },
        { text: 'Nay em nghỉ 💤 (Test)', callback_data: 'test_off' }
      ]
    ]
  };

  const url = `https://api.telegram.org/bot${botToken}/sendMessage`;
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: chatId,
        text: 'Đến giờ uống thuốc rồi em iu ơi! 🌸 (BẢN THỬ NGHIỆM - Bấm nút này sẽ không lưu lịch sử)',
        reply_markup: replyMarkup
      })
    });

    if (!response.ok) {
      const errText = await response.text();
      return res.status(500).json({ error: `Telegram error: ${errText}` });
    }

    return res.status(200).json({ success: true });
  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
}
