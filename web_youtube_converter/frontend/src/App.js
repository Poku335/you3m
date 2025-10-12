import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '/api' 
  : 'http://localhost:8000/api';

function App() {
  const [url, setUrl] = useState('');
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [videoInfo, setVideoInfo] = useState(null);
  const [step, setStep] = useState(1); // 1 = ใส่ URL, 2 = แสดงข้อมูลวิดีโอ


  useEffect(() => {
    clearAllTasks().then(fetchTasks);

    const handleBeforeUnload = () => {
      navigator.sendBeacon(`${API_BASE_URL}/clear/`, '{}');
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, []);

  useEffect(() => {
    const hasProcessingTasks = tasks.some(task =>
      task.status === 'pending' || task.status === 'processing'
    );

    if (!hasProcessingTasks && tasks.length > 0) return;

    const interval = setInterval(fetchTasks, 5000);
    return () => clearInterval(interval);
  }, [tasks]);

  const fetchTasks = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/tasks/`);
      setTasks(response.data);
    } catch (error) {
      console.error('Error fetching tasks:', error);
    }
  };

  const clearAllTasks = async () => {
    try {
      await axios.post(`${API_BASE_URL}/clear/`);
      setTasks([]);
    } catch (error) {
      console.error('Error clearing tasks:', error);
    }
  };



  const handleGetVideoInfo = async (e) => {
    e.preventDefault();
    if (!url.trim()) return;

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/video-info/`, {
        youtube_url: url
      });
      setVideoInfo(response.data);
      setStep(2);
    } catch (error) {
      console.error('Error getting video info:', error);
      alert('ไม่สามารถดึงข้อมูลวิดีโอได้ กรุณาตรวจสอบลิงก์');
    } finally {
      setLoading(false);
    }
  };

  const handleStartConversion = async () => {
    setLoading(true);
    try {
      await axios.post(`${API_BASE_URL}/convert/`, {
        youtube_url: url
      });
      setStep(1);
      setUrl('');
      setVideoInfo(null);
      fetchTasks();
    } catch (error) {
      console.error('Error starting conversion:', error);
      alert('เกิดข้อผิดพลาดในการเริ่มแปลงไฟล์');
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    setStep(1);
    setVideoInfo(null);
  };

  const handleDownload = async (taskId, title) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/download/${taskId}/`, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.download = `${title}.mp3`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      alert('เกิดข้อผิดพลาดในการดาวน์โหลดไฟล์');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-600';
      case 'processing': return 'text-blue-600';
      case 'failed': return 'text-red-600';
      default: return 'text-yellow-600';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'pending': return 'รอดำเนินการ';
      case 'processing': return 'กำลังประมวลผล';
      case 'completed': return 'เสร็จสิ้น';
      case 'failed': return 'ล้มเหลว';
      default: return status;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-800 mb-2">
              แปลง YouTube เป็น MP3
            </h1>
            <p className="text-gray-600">
              ดาวน์โหลดเสียงจาก YouTube ได้ง่ายๆ
            </p>
          </div>

          {/* Form */}
          <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
            {step === 1 ? (
              <form onSubmit={handleGetVideoInfo} className="space-y-4">
                <div>
                  <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-2">
                    ลิงก์ YouTube
                  </label>
                  <input
                    type="url"
                    id="url"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="https://www.youtube.com/watch?v=..."
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium py-3 px-6 rounded-lg transition duration-200"
                >
                  {loading ? 'กำลังดึงข้อมูล...' : 'แปลงไฟล์'}
                </button>
              </form>
            ) : (
              <div className="space-y-6">
                {/* Video Info Display */}
                <div className="flex items-start space-x-4">
                  <img
                    src={videoInfo?.thumbnail}
                    alt="Video thumbnail"
                    className="w-32 h-24 object-cover rounded-lg shadow-md"
                    onError={(e) => {
                      e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTI4IiBoZWlnaHQ9Ijk2IiB2aWV3Qm94PSIwIDAgMTI4IDk2IiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8cmVjdCB3aWR0aD0iMTI4IiBoZWlnaHQ9Ijk2IiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik02NCA0OEw3NiA1Nkw2NCA2NEw1MiA1Nkw2NCA0OFoiIGZpbGw9IiM5Q0EzQUYiLz4KPC9zdmc+';
                    }}
                  />
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-800 mb-2">
                      {videoInfo?.title}
                    </h3>
                    <p className="text-sm text-gray-600 mb-1">
                      ผู้อัพโหลด: {videoInfo?.uploader}
                    </p>
                    {videoInfo?.duration && (
                      <p className="text-sm text-gray-600 mb-1">
                        ระยะเวลา: {Math.floor(videoInfo.duration / 60)}:{(videoInfo.duration % 60).toString().padStart(2, '0')} นาที
                      </p>
                    )}
                    {videoInfo?.view_count && (
                      <p className="text-sm text-gray-600">
                        จำนวนผู้ชม: {videoInfo.view_count.toLocaleString()} ครั้ง
                      </p>
                    )}
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex space-x-4">
                  <button
                    onClick={handleBack}
                    className="flex-1 bg-gray-500 hover:bg-gray-600 text-white font-medium py-3 px-6 rounded-lg transition duration-200"
                  >
                    กลับ
                  </button>
                  <button
                    onClick={handleStartConversion}
                    disabled={loading}
                    className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white font-medium py-3 px-6 rounded-lg transition duration-200"
                  >
                    {loading ? 'กำลังแปลง...' : 'แปลงเป็น MP3'}
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Tasks List */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">
              รายการ
            </h2>

            {tasks.length === 0 ? (
              <p className="text-gray-500 text-center py-8">
                ยังไม่มีงานในระบบ
              </p>
            ) : (
              <div className="space-y-4">
                {tasks.map((task) => (
                  <div key={task.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-medium text-gray-800 truncate flex-1 mr-4">
                        {task.title || 'กำลังโหลดชื่อ...'}
                      </h3>
                      <span className={`text-sm font-medium ${getStatusColor(task.status)}`}>
                        {getStatusText(task.status)}
                      </span>
                    </div>

                    {task.status === 'processing' && (
                      <div className="mb-3">
                        <div className="flex justify-between text-sm text-gray-600 mb-1">
                          <span>ความคืบหน้า</span>
                          <span>{task.progress}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${task.progress}%` }}
                          ></div>
                        </div>
                      </div>
                    )}

                    {task.error_message && (
                      <p className="text-red-600 text-sm mb-2">
                        {task.error_message}
                      </p>
                    )}

                    <div className="flex items-center justify-end">

                      {task.status === 'completed' && (
                        <button
                          onClick={() => handleDownload(task.id, task.title)}
                          className="bg-green-600 hover:bg-green-700 text-white text-sm font-medium py-2 px-4 rounded-lg transition duration-200"
                        >
                          ดาวน์โหลด
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;