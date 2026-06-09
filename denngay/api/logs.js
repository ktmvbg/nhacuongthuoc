export default async function handler(req, res) {
  // CORS Headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const token = process.env.GITHUB_TOKEN;
  const owner = 'ktmvbg';
  const repo = 'nhacuongthuoc';
  const path = 'db.json';

  const url = `https://api.github.com/repos/${owner}/${repo}/contents/${path}`;
  const headers = {
    'Authorization': `token ${token}`,
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'Vercel-Serverless'
  };

  // Hàm đọc file db.json từ GitHub
  async function getFile() {
    try {
      const response = await fetch(url, { 
        headers,
        cache: 'no-store'
      });
      if (response.status === 404) {
        return { content: [], sha: null };
      }
      if (!response.ok) {
        throw new Error(`GitHub GET error: ${response.statusText}`);
      }
      const data = await response.json();
      const decoded = Buffer.from(data.content, 'base64').toString('utf-8');
      return { content: JSON.parse(decoded), sha: data.sha };
    } catch (err) {
      console.error(err);
      return { content: [], sha: null };
    }
  }

  if (req.method === 'GET') {
    res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
    res.setHeader('Pragma', 'no-cache');
    res.setHeader('Expires', '0');
    const { content } = await getFile();
    // Trả về danh sách logs sắp xếp từ mới nhất đến cũ nhất
    const sorted = content.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    return res.status(200).json(sorted);
  }

  if (req.method === 'POST') {
    const { status, note, created_at } = req.body;
    if (!status) {
      return res.status(400).json({ error: 'Missing status' });
    }

    const { content, sha } = await getFile();
    
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

    const rawDateStr = created_at || new Date().toISOString();
    const targetDateStr = getAdjustedTimestamp(rawDateStr);

    // Tạo bản ghi mới, hỗ trợ custom created_at
    const newLog = {
      id: Math.random().toString(36).substring(2),
      created_at: targetDateStr,
      status,
      note: note || null
    };

    let updatedContent = content;
    if (status === 'taken' || status === 'off') {
      // Lọc bỏ tất cả các log của ngày targetDateStr trước khi lưu trạng thái 'taken' hoặc 'off'
      updatedContent = content.filter(log => !isSameDayVN(log.created_at, targetDateStr));
    }

    updatedContent.push(newLog);
    const updatedContentB64 = Buffer.from(JSON.stringify(updatedContent, null, 2)).toString('base64');

    const body = {
      message: status === 'taken' ? 'Register taken and clean daily logs via web' : 
               status === 'off' ? 'Register off and clean daily logs via web' : 'Add medicine log via web',
      content: updatedContentB64,
    };
    if (sha) {
      body.sha = sha;
    }

    const putResponse = await fetch(url, {
      method: 'PUT',
      headers: {
        ...headers,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    });

    if (!putResponse.ok) {
      const errText = await putResponse.text();
      return res.status(500).json({ error: `GitHub PUT error: ${errText}` });
    }

    return res.status(201).json(newLog);
  }

  if (req.method === 'DELETE') {
    const { id } = req.body;
    if (!id) {
      return res.status(400).json({ error: 'Missing id' });
    }

    const { content, sha } = await getFile();
    
    // Lọc bỏ bản ghi cần xóa
    const updatedContent = content.filter((log) => log.id !== id);
    const updatedContentB64 = Buffer.from(JSON.stringify(updatedContent, null, 2)).toString('base64');

    const body = {
      message: 'Delete medicine log via web',
      content: updatedContentB64,
    };
    if (sha) {
      body.sha = sha;
    }

    const putResponse = await fetch(url, {
      method: 'PUT',
      headers: {
        ...headers,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    });

    if (!putResponse.ok) {
      const errText = await putResponse.text();
      return res.status(500).json({ error: `GitHub PUT error: ${errText}` });
    }

    return res.status(200).json({ success: true });
  }

  return res.status(405).json({ error: 'Method not allowed' });
}
