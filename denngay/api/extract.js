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

    return res.status(200).json(data);
  } catch (err) {
    console.error('Extraction Error:', err.message);
    return res.status(500).json({
      error: 'Failed to extract data from Stardust',
      details: err.message
    });
  }
}
