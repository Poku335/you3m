const { exec } = require('child_process');
const { promisify } = require('util');
const fs = require('fs');
const path = require('path');
const execAsync = promisify(exec);

// In-memory storage for tasks (in production, use a database)
let tasks = [];
let taskIdCounter = 1;

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
    // สร้าง task ใหม่
    const taskId = taskIdCounter++;
    const task = {
      id: taskId,
      youtube_url,
      status: 'pending',
      progress: 0,
      title: null,
      file_path: null,
      created_at: new Date().toISOString()
    };

    tasks.push(task);

    // เริ่มการแปลงไฟล์ (async)
    processConversion(taskId, youtube_url);

    res.status(200).json({ 
      message: 'Conversion started',
      task_id: taskId 
    });
  } catch (error) {
    console.error('Error starting conversion:', error);
    res.status(500).json({ 
      error: 'Failed to start conversion',
      details: error.message 
    });
  }
}

async function processConversion(taskId, youtubeUrl) {
  const task = tasks.find(t => t.id === taskId);
  if (!task) return;

  try {
    task.status = 'processing';
    task.progress = 10;

    // สร้างโฟลเดอร์ temp
    const tempDir = '/tmp';
    const outputPath = path.join(tempDir, `audio_${taskId}.mp3`);

    // ดึงข้อมูลวิดีโอ
    const infoCommand = `yt-dlp --dump-json --no-download "${youtubeUrl}"`;
    const { stdout } = await execAsync(infoCommand);
    const videoData = JSON.parse(stdout);
    
    task.title = videoData.title;
    task.progress = 30;

    // แปลงเป็น MP3
    const convertCommand = `yt-dlp -x --audio-format mp3 --audio-quality 0 -o "${outputPath.replace('.mp3', '.%(ext)s')}" "${youtubeUrl}"`;
    
    await execAsync(convertCommand);
    
    task.progress = 90;
    task.file_path = outputPath;
    task.status = 'completed';
    task.progress = 100;

  } catch (error) {
    console.error('Conversion error:', error);
    task.status = 'failed';
    task.error_message = error.message;
  }
}

// Export tasks for other API routes
export { tasks };