export default async function handler(req, res) {
  // CORS Headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

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
        id_token: id_token,
        app_id: 'b6b8e7c0-fb66-4c6c-a391-bbf0a7d8dfcc'
      })
    });

    const data = await response.json();
    if (!response.ok) {
      return res.status(response.status).json({ error: 'Failed to authenticate with Rownd', details: data });
    }

    return res.status(200).json(data);
  } catch (err) {
    console.error('Authentication Error:', err.message);
    return res.status(500).json({
      error: 'Failed to authenticate with Rownd',
      details: err.message
    });
  }
}
