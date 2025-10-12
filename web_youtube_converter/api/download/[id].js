const fs = require('fs');
const path = require('path');

// Import tasks (in production, use database)
let tasks = [];

export default async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { id } = req.query;
  const taskId = parseInt(id);

  try {
    const task = tasks.find(t => t.id === taskId);
    
    if (!task) {
      return res.status(404).json({ error: 'Task not found' });
    }

    if (task.status !== 'completed' || !task.file_path) {
      return res.status(400).json({ error: 'File not ready for download' });
    }

    if (!fs.existsSync(task.file_path)) {
      return res.status(404).json({ error: 'File not found' });
    }

    const fileBuffer = fs.readFileSync(task.file_path);
    const fileName = `${task.title || 'audio'}.mp3`;

    res.setHeader('Content-Type', 'audio/mpeg');
    res.setHeader('Content-Disposition', `attachment; filename="${fileName}"`);
    res.setHeader('Content-Length', fileBuffer.length);

    res.status(200).send(fileBuffer);

    // ลบไฟล์หลังดาวน์โหลด (optional)
    setTimeout(() => {
      try {
        if (fs.existsSync(task.file_path)) {
          fs.unlinkSync(task.file_path);
        }
      } catch (error) {
        console.error('Error deleting file:', error);
      }
    }, 5000);

  } catch (error) {
    console.error('Error downloading file:', error);
    res.status(500).json({ 
      error: 'Failed to download file',
      details: error.message 
    });
  }
}