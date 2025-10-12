const fs = require('fs');

// Import tasks
let tasks = [];

export default async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // ลบไฟล์ที่เหลืออยู่
    tasks.forEach(task => {
      if (task.file_path && fs.existsSync(task.file_path)) {
        try {
          fs.unlinkSync(task.file_path);
        } catch (error) {
          console.error('Error deleting file:', error);
        }
      }
    });

    // ล้าง tasks
    tasks.length = 0;

    res.status(200).json({ message: 'All tasks cleared' });
  } catch (error) {
    console.error('Error clearing tasks:', error);
    res.status(500).json({ 
      error: 'Failed to clear tasks',
      details: error.message 
    });
  }
}