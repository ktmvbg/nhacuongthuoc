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
      const response = await fetch(url, { headers });
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
    
    // Tạo bản ghi mới, hỗ trợ custom created_at
    const newLog = {
      id: Math.random().toString(36).substring(2),
      created_at: created_at || new Date().toISOString(),
      status,
      note: note || null
    };

    content.push(newLog);
    const updatedContentB64 = Buffer.from(JSON.stringify(content, null, 2)).toString('base64');

    const body = {
      message: 'Add medicine log via web',
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
