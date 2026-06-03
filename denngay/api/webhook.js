export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const token = process.env.GITHUB_TOKEN;
  const botToken = process.env.TELEGRAM_BOT_TOKEN;
  const owner = 'ktmvbg';
  const repo = 'nhacuongthuoc';
  const path = 'db.json';

  const body = req.body;
  if (!body.callback_query) {
    // Không phải sự kiện bấm nút, trả về OK để Telegram biết đã nhận tin
    return res.status(200).send('OK');
  }

  const callbackQuery = body.callback_query;
  const callbackData = callbackQuery.data;
  const chatId = callbackQuery.message.chat.id;
  const messageId = callbackQuery.message.message_id;

  const url = `https://api.github.com/repos/${owner}/${repo}/contents/${path}`;
  const gitHeaders = {
    'Authorization': `token ${token}`,
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'Vercel-Serverless'
  };

  // Đọc file db.json hiện tại từ GitHub
  async function getFile() {
    try {
      const response = await fetch(url, { headers: gitHeaders });
      if (response.status === 404) {
        return { content: [], sha: null };
      }
      const data = await response.json();
      const decoded = Buffer.from(data.content, 'base64').toString('utf-8');
      return { content: JSON.parse(decoded), sha: data.sha };
    } catch (err) {
      return { content: [], sha: null };
    }
  }

  // Ghi log vào file db.json trên GitHub
  async function saveLog(status) {
    const { content, sha } = await getFile();
    const newLog = {
      id: Math.random().toString(36).substring(2),
      created_at: new Date().toISOString(),
      status,
      note: 'Ghi nhận qua Telegram Bot'
    };
    content.push(newLog);
    const updatedContentB64 = Buffer.from(JSON.stringify(content, null, 2)).toString('base64');
    const putBody = {
      message: 'Add medicine log via Telegram',
      content: updatedContentB64,
    };
    if (sha) putBody.sha = sha;

    await fetch(url, {
      method: 'PUT',
      headers: { ...gitHeaders, 'Content-Type': 'application/json' },
      body: JSON.stringify(putBody)
    });
  }

  // Hàm chỉnh sửa tin nhắn Telegram
  async function editMessageText(text, replyMarkup) {
    const editUrl = `https://api.telegram.org/bot${botToken}/editMessageText`;
    await fetch(editUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: chatId,
        message_id: messageId,
        text,
        reply_markup: replyMarkup
      })
    });
  }

  // Hàm phản hồi callback cho Telegram
  async function answerCallbackQuery(text) {
    const answerUrl = `https://api.telegram.org/bot${botToken}/answerCallbackQuery`;
    await fetch(answerUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        callback_query_id: callbackQuery.id,
        text
      })
    });
  }

  // Múi giờ Việt Nam khi hiển thị tin nhắn
  const nowStr = new Date().toLocaleTimeString('vi-VN', {
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'Asia/Ho_Chi_Minh'
  });

  if (callbackData === 'taken') {
    await saveLog('taken');
    await editMessageText(`Tuyệt vời! Anh ghi nhận em đã uống thuốc lúc ${nowStr} rồi nhé. Ngoan lắm! 💕`);
    await answerCallbackQuery('Đã ghi nhận uống thuốc! 🌸');
    
  } else if (callbackData === 'later') {
    await saveLog('delayed');
    const replyMarkup = {
      inline_keyboard: [
        [{ text: 'Đã uống 🌸', callback_data: 'taken' }]
      ]
    };
    await editMessageText('Oki em iu, nhớ uống thuốc nhé! Khi nào uống xong em bấm nút "Đã uống 🌸" dưới đây nha. ⏰', replyMarkup);
    await answerCallbackQuery('Đã hẹn tí nữa uống!');

    // Kích hoạt GitHub Action workflow báo lại sau 10 phút
    try {
      const triggerUrl = `https://api.github.com/repos/${owner}/${repo}/actions/workflows/snooze.yml/dispatches`;
      await fetch(triggerUrl, {
        method: 'POST',
        headers: {
          'Authorization': `token ${token}`,
          'Accept': 'application/vnd.github.v3+json',
          'User-Agent': 'Vercel-Serverless',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ref: 'main',
          inputs: {
            chat_id: String(chatId)
          }
        })
      });
      console.log('Đã kích hoạt snooze workflow.');
    } catch (err) {
      console.error('Lỗi khi kích hoạt snooze workflow:', err.message);
    }
    
  } else if (callbackData === 'test_taken') {
    // Không ghi nhận log vào DB
    await editMessageText(`[Test] Tuyệt vời! Anh ghi nhận em đã uống thuốc lúc ${nowStr} rồi nhé. (Không ghi vào DB) 💕`);
    await answerCallbackQuery('Test thành công! 🌸');
    
  } else if (callbackData === 'test_later') {
    // Không ghi nhận log vào DB
    const replyMarkup = {
      inline_keyboard: [
        [{ text: 'Đã uống 🌸 (Test)', callback_data: 'test_taken' }]
      ]
    };
    await editMessageText('Oki em iu, nhớ uống thuốc nhé! Khi nào uống xong em bấm nút "Đã uống (Test)" dưới đây nha. ⏰ (Bản thử nghiệm)', replyMarkup);
    await answerCallbackQuery('Test hẹn tí nữa thành công!');
  }

  return res.status(200).send('OK');
}
