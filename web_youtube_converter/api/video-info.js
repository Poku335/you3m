const { exec } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);

export default async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { youtube_url } = req.body;

  if (!youtube_url) {
    return res.status(400).json({ error: 'YouTube URL is required' });
  }

  try {
    // ใช้ yt-dlp เพื่อดึงข้อมูลวิดีโอ
    const command = `yt-dlp --dump-json --no-download "${youtube_url}"`;
    const { stdout } = await execAsync(command);
    
    const videoData = JSON.parse(stdout);
    
    const videoInfo = {
      title: videoData.title,
      uploader: videoData.uploader,
      duration: videoData.duration,
      view_count: videoData.view_count,
      thumbnail: videoData.thumbnail
    };

    res.status(200).json(videoInfo);
  } catch (error) {
    console.error('Error getting video info:', error);
    res.status(500).json({ 
      error: 'Failed to get video information',
      details: error.message 
    });
  }
}