export default async function handler(req, res) {
  // Allow GET to be triggered by Vercel Cron, and POST for testing
  if (req.method !== 'GET' && req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  // Secure the endpoint if CRON_SECRET is set in Vercel environment variables
  if (process.env.CRON_SECRET) {
    const authHeader = req.headers.authorization;
    if (authHeader !== `Bearer ${process.env.CRON_SECRET}`) {
      return res.status(401).json({ error: 'Unauthorized' });
    }
  }

  const botToken = process.env.TELEGRAM_BOT_TOKEN;
  const chatId = process.env.TELEGRAM_CHAT_ID;

  if (!botToken || !chatId) {
    return res.status(500).json({ error: 'Thiếu cấu hình Telegram Token hoặc Chat ID' });
  }

  // Define interactive buttons
  const replyMarkup = {
    inline_keyboard: [
      [
        { text: "Đã uống 🌸", callback_data: "taken" },
        { text: "Để tí nữa ⏰", callback_data: "later" },
        { text: "Nay em nghỉ 💤", callback_data: "off" }
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
        text: "Đến giờ uống thuốc rồi em iu ơi! 🌸",
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
