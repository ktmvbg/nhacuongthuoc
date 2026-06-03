import express from 'express';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load environment variables from the .env file in the root directory
dotenv.config({ path: path.resolve(__dirname, '../.env') });

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

// Serve static built files from the React dist folder
app.use(express.static(path.resolve(__dirname, 'dist')));

// GET /api/logs
app.get('/api/logs', async (req, res) => {
  const token = process.env.GITHUB_TOKEN;
  const owner = 'ktmvbg';
  const repo = 'nhacuongthuoc';
  const filepath = 'db.json';
  const url = `https://api.github.com/repos/${owner}/${repo}/contents/${filepath}`;

  try {
    const response = await fetch(url, {
      headers: {
        'Authorization': `token ${token}`,
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'Local-Server'
      }
    });

    if (response.status === 404) {
      return res.json([]);
    }

    if (!response.ok) {
      throw new Error(`GitHub GET error: ${response.statusText}`);
    }

    const data = await response.json();
    const decoded = Buffer.from(data.content, 'base64').toString('utf-8');
    const logs = JSON.parse(decoded);
    const sorted = logs.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    res.json(sorted);
  } catch (err) {
    console.error('Error getting logs:', err.message);
    res.status(500).json({ error: err.message });
  }
});

// POST /api/logs
app.post('/api/logs', async (req, res) => {
  const { status, note, created_at } = req.body;
  if (!status) {
    return res.status(400).json({ error: 'Missing status' });
  }

  const token = process.env.GITHUB_TOKEN;
  const owner = 'ktmvbg';
  const repo = 'nhacuongthuoc';
  const filepath = 'db.json';
  const url = `https://api.github.com/repos/${owner}/${repo}/contents/${filepath}`;
  const headers = {
    'Authorization': `token ${token}`,
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'Local-Server'
  };

  try {
    let content = [];
    let sha = null;

    const getRes = await fetch(url, { headers });
    if (getRes.ok) {
      const getRaw = await getRes.json();
      sha = getRaw.sha;
      const decoded = Buffer.from(getRaw.content, 'base64').toString('utf-8');
      content = JSON.parse(decoded);
    }

    const newLog = {
      id: Math.random().toString(36).substring(2),
      created_at: created_at || new Date().toISOString(),
      status,
      note: note || null
    };

    content.push(newLog);
    const updatedContentB64 = Buffer.from(JSON.stringify(content, null, 2)).toString('base64');

    const body = {
      message: 'Add medicine log via local dev',
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

    res.status(201).json(newLog);
  } catch (err) {
    console.error('Error posting log:', err.message);
    res.status(500).json({ error: err.message });
  }
});

// DELETE /api/logs
app.delete('/api/logs', async (req, res) => {
  const { id } = req.body;
  if (!id) {
    return res.status(400).json({ error: 'Missing id' });
  }

  const token = process.env.GITHUB_TOKEN;
  const owner = 'ktmvbg';
  const repo = 'nhacuongthuoc';
  const filepath = 'db.json';
  const url = `https://api.github.com/repos/${owner}/${repo}/contents/${filepath}`;
  const headers = {
    'Authorization': `token ${token}`,
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'Local-Server'
  };

  try {
    let content = [];
    let sha = null;

    const getRes = await fetch(url, { headers });
    if (getRes.ok) {
      const getRaw = await getRes.json();
      sha = getRaw.sha;
      const decoded = Buffer.from(getRaw.content, 'base64').toString('utf-8');
      content = JSON.parse(decoded);
    }

    const updatedContent = content.filter((log) => log.id !== id);
    const updatedContentB64 = Buffer.from(JSON.stringify(updatedContent, null, 2)).toString('base64');

    const body = {
      message: 'Delete medicine log via local dev',
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

    res.json({ success: true });
  } catch (err) {
    console.error('Error deleting log:', err.message);
    res.status(500).json({ error: err.message });
  }
});

// POST /api/authenticate (Exchanges Google ID token for Rownd access token)
app.post('/api/authenticate', async (req, res) => {
  const { id_token } = req.body;
  if (!id_token) {
    return res.status(400).json({ error: 'id_token is required' });
  }

  try {
    const response = await fetch('https://api.rownd.io/hub/auth/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0'
      },
      body: JSON.stringify({
        id_token,
        app_id: 'b6b8e7c0-fb66-4c6c-a391-bbf0a7d8dfcc'
      })
    });

    const data = await response.json();
    if (!response.ok) {
      return res.status(response.status).json({ error: 'Failed to authenticate with Rownd', details: data });
    }

    res.json(data);
  } catch (err) {
    res.status(500).json({ error: 'Failed to authenticate with Rownd', details: err.message });
  }
});

// POST /api/extract (Extracts period/ovulation data from Stardust)
app.post('/api/extract', async (req, res) => {
  const { access_token } = req.body;
  if (!access_token) {
    return res.status(400).json({ error: 'access_token is required' });
  }

  try {
    const response = await fetch('https://api.stardust.app/api/v2/my-logs', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${access_token}`,
        'User-Agent': 'Stardust/5.21.0 (Android; SDK 33)',
        'Accept': 'application/json'
      }
    });

    const data = await response.json();
    if (!response.ok) {
      return res.status(response.status).json({ error: 'Failed to extract data from Stardust', details: data });
    }

    res.json(data);
  } catch (err) {
    res.status(500).json({ error: 'Failed to extract data from Stardust', details: err.message });
  }
});

// POST /api/test-reminder (SendsTelegram test reminder)
app.post('/api/test-reminder', async (req, res) => {
  const botToken = process.env.TELEGRAM_BOT_TOKEN;
  const chatId = process.env.TELEGRAM_CHAT_ID;

  if (!botToken || !chatId) {
    return res.status(400).json({ error: 'Telegram credentials missing' });
  }

  try {
    const response = await fetch(`https://api.telegram.org/bot${botToken}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: chatId,
        text: '🌸 Quỳnh ơi, đây là tin nhắn nhắc nhở thử nghiệm từ web app của bạn! Uống thuốc đúng giờ nhé!'
      })
    });

    const data = await response.json();
    if (!response.ok) {
      return res.status(response.status).json({ error: 'Failed to send Telegram reminder', details: data });
    }

    res.json(data);
  } catch (err) {
    res.status(500).json({ error: 'Failed to send Telegram reminder', details: err.message });
  }
});

// Fallback for React Router / SPA routing: serve index.html for all other routes
app.get('*', (req, res) => {
  res.sendFile(path.resolve(__dirname, 'dist', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`\n===================================================`);
  console.log(`  nhacuongthuoc web app offline running successfully!`);
  console.log(`  - Giao dien web: http://localhost:${PORT}`);
  console.log(`===================================================\n`);
});
