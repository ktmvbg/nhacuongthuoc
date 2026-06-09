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

  // Helper kiểm tra xem hai mốc thời gian có cùng ngày theo giờ Việt Nam (GMT+7) không
  function isSameDayVN(dateStr1, dateStr2) {
    try {
      const d1 = new Date(dateStr1);
      const d2 = new Date(dateStr2);
      const getVNString = (d) => d.toLocaleDateString('en-US', {
        timeZone: 'Asia/Ho_Chi_Minh',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      });
      return getVNString(d1) === getVNString(d2);
    } catch (e) {
      return false;
    }
  }

  // Helper dịch chuyển thời gian về ngày hôm trước nếu giờ Việt Nam < 12:00 trưa (trước 12h trưa)
  function getAdjustedTimestamp(dateStr) {
    try {
      const date = new Date(dateStr);
      // Giờ Việt Nam bằng giờ UTC cộng 7 tiếng
      const vnTime = new Date(date.getTime() + 7 * 60 * 60 * 1000);
      const vnHour = vnTime.getUTCHours();
      if (vnHour < 12) {
        // Trừ đi 24 giờ để lùi lại 1 ngày
        return new Date(date.getTime() - 24 * 60 * 60 * 1000).toISOString();
      }
      return date.toISOString();
    } catch (e) {
      return dateStr;
    }
  }

  // Ghi log vào file db.json trên GitHub
  async function saveLog(status) {
    const { content, sha } = await getFile();
    const now = new Date();
    const targetDateStr = getAdjustedTimestamp(now.toISOString());
    const newLog = {
      id: Math.random().toString(36).substring(2),
      created_at: targetDateStr,
      status,
      note: 'Ghi nhận qua Telegram Bot'
    };

    let updatedContent = content;
    if (status === 'taken' || status === 'off') {
      // Lọc bỏ tất cả các log của ngày targetDateStr (giờ VN) trước khi lưu trạng thái 'taken' hoặc 'off'
      updatedContent = content.filter(log => !isSameDayVN(log.created_at, targetDateStr));
    }

    updatedContent.push(newLog);
    const updatedContentB64 = Buffer.from(JSON.stringify(updatedContent, null, 2)).toString('base64');
    const putBody = {
      message: status === 'taken' ? 'Register taken and clean daily logs' : 
               status === 'off' ? 'Register off and clean daily logs' : 'Add medicine log via Telegram',
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
    
  } else if (callbackData === 'off') {
    await saveLog('off');
    await editMessageText(`Anh ghi nhận hôm nay em nghỉ ngơi uống thuốc nhé! Nghỉ khỏe nha em iu 💤`);
    await answerCallbackQuery('Đã ghi nhận nghỉ uống thuốc! 💤');

  } else if (callbackData === 'later') {
    await saveLog('delayed');
    const replyMarkup = {
      inline_keyboard: [
        [
          { text: 'Đã uống 🌸', callback_data: 'taken' },
          { text: 'Nay em nghỉ 💤', callback_data: 'off' }
        ]
      ]
    };
    await editMessageText('Oki em iu, nhớ uống thuốc nhé! Khi nào uống hoặc nghỉ em chọn ở nút dưới nha. ⏰', replyMarkup);
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
    
  } else if (callbackData === 'test_off') {
    // Không ghi nhận log vào DB
    await editMessageText(`[Test] Anh ghi nhận hôm nay em nghỉ ngơi uống thuốc nhé! (Không ghi vào DB) 💤`);
    await answerCallbackQuery('Test nghỉ uống thuốc thành công!');

  } else if (callbackData === 'test_later') {
    // Không ghi nhận log vào DB
    const replyMarkup = {
      inline_keyboard: [
        [
          { text: 'Đã uống 🌸 (Test)', callback_data: 'test_taken' },
          { text: 'Nay em nghỉ 💤 (Test)', callback_data: 'test_off' }
        ]
      ]
    };
    await editMessageText('Oki em iu, nhớ uống thuốc nhé! Khi nào uống xong hoặc nghỉ em bấm nút dưới nha. ⏰ (Bản thử nghiệm)', replyMarkup);
    await answerCallbackQuery('Test hẹn tí nữa thành công!');
  }

  return res.status(200).send('OK');
}
