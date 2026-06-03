import React, { useState, useEffect } from 'react';

// URL của Server Bot (Mặc định để trống sẽ dùng đường dẫn tương đối của Vercel)
const API_URL = import.meta.env.VITE_API_URL || '';

// Hàm lấy ngày hiện tại (YYYY-MM-DD) theo múi giờ địa phương
const getLocalDateString = () => {
  const d = new Date();
  const offset = d.getTimezoneOffset();
  const local = new Date(d.getTime() - (offset * 60 * 1000));
  return local.toISOString().split('T')[0];
};

// Hàm lấy giờ hiện tại (HH:MM) theo múi giờ địa phương
const getLocalTimeString = () => {
  const d = new Date();
  const hh = String(d.getHours()).padStart(2, '0');
  const mm = String(d.getMinutes()).padStart(2, '0');
  return `${hh}:${mm}`;
};

function App() {
  const [logs, setLogs] = useState([]);
  const [streak, setStreak] = useState(0);
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [isLoading, setIsLoading] = useState(true);
  const [formStatus, setFormStatus] = useState('taken');
  const [formDate, setFormDate] = useState(getLocalDateString());
  const [formTime, setFormTime] = useState(getLocalTimeString());
  const [formNote, setFormNote] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    fetchLogs();
  }, []);

  useEffect(() => {
    if (logs.length > 0) {
      calculateStreak(logs);
    } else {
      setStreak(0);
    }
  }, [logs]);

  const fetchLogs = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/logs`);
      if (!response.ok) {
        throw new Error('Lỗi phản hồi từ máy chủ API');
      }
      const data = await response.json();
      setLogs(data || []);
    } catch (err) {
      console.error('Lỗi khi tải lịch sử:', err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const calculateStreak = (allLogs) => {
    // Chỉ tính các ngày có trạng thái "taken" (Đã uống)
    const takenDates = allLogs
      .filter((log) => log.status === 'taken')
      .map((log) => {
        const d = new Date(log.created_at);
        return new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime();
      });

    if (takenDates.length === 0) {
      setStreak(0);
      return;
    }

    // Lọc trùng và sắp xếp giảm dần (ngày gần nhất trước)
    const sortedUniqueDates = [...new Set(takenDates)].sort((a, b) => b - a);

    let currentStreak = 0;
    const today = new Date();
    const todayMidnight = new Date(today.getFullYear(), today.getMonth(), today.getDate()).getTime();
    
    const yesterdayMidnight = todayMidnight - 24 * 60 * 60 * 1000;

    // Nếu ngày gần nhất không phải hôm nay hoặc hôm qua, streak bằng 0 (bị đứt đoạn)
    const mostRecent = sortedUniqueDates[0];
    if (mostRecent !== todayMidnight && mostRecent !== yesterdayMidnight) {
      setStreak(0);
      return;
    }

    let expectedDate = mostRecent;
    for (let i = 0; i < sortedUniqueDates.length; i++) {
      if (sortedUniqueDates[i] === expectedDate) {
        currentStreak++;
        expectedDate -= 24 * 60 * 60 * 1000; // Trừ đi 1 ngày
      } else {
        break; // Bị đứt đoạn
      }
    }
    setStreak(currentStreak);
  };

  const handleManualSubmit = async (e) => {
    e.preventDefault();
    if (isSubmitting) return;

    setIsSubmitting(true);
    try {
      // Ghép ngày và giờ được chọn thành định dạng ISO để gửi lên server
      const localDateTime = new Date(`${formDate}T${formTime}`);
      const created_at = localDateTime.toISOString();

      const response = await fetch(`${API_URL}/api/logs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          status: formStatus,
          note: formNote || null,
          created_at
        })
      });

      if (!response.ok) {
        throw new Error('Không thể thêm lịch sử lên máy chủ');
      }

      setFormNote('');
      setFormDate(getLocalDateString());
      setFormTime(getLocalTimeString());
      await fetchLogs();
      alert('Đã cập nhật lịch sử uống thuốc thành công! 🌸');
    } catch (err) {
      alert('Không thể lưu: ' + err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Hàm xóa bản ghi lịch sử
  const handleDeleteLog = async (id) => {
    if (!window.confirm('Bạn có chắc chắn muốn xóa bản ghi này không? 🌸')) return;

    try {
      const response = await fetch(`${API_URL}/api/logs`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id })
      });

      if (!response.ok) {
        throw new Error('Lỗi từ máy chủ khi xóa bản ghi');
      }

      await fetchLogs();
      alert('Đã xóa bản ghi thành công! 🌸');
    } catch (err) {
      alert('Không thể xóa: ' + err.message);
    }
  };

  // Hàm gửi tin nhắn nhắc nhở thử nghiệm
  const handleSendTestReminder = async () => {
    try {
      const response = await fetch(`${API_URL}/api/test-reminder`, {
        method: 'POST'
      });
      if (!response.ok) {
        throw new Error('Không thể gửi tin nhắn thử nghiệm');
      }
      alert('Đã gửi tin nhắn nhắc nhở thử nghiệm tới Telegram! 🚀');
    } catch (err) {
      alert('Gửi tin nhắn thử nghiệm thất bại: ' + err.message);
    }
  };

  // Các hàm tính toán cho Calendar
  const getDaysInMonth = (date) => {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
  };

  const getFirstDayOfMonth = (date) => {
    return new Date(date.getFullYear(), date.getMonth(), 1).getDay();
  };

  const handlePrevMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1));
  };

  const handleNextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1));
  };

  const renderCalendar = () => {
    const daysInMonth = getDaysInMonth(currentMonth);
    const firstDay = getFirstDayOfMonth(currentMonth);
    const cells = [];

    // Cell trống của tháng trước
    for (let i = 0; i < firstDay; i++) {
      cells.push(<div key={`empty-${i}`} className="calendar-cell empty"></div>);
    }

    // Các ngày trong tháng hiện tại
    for (let day = 1; day <= daysInMonth; day++) {
      const cellDate = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), day);
      
      // Tìm xem ngày này có log nào không
      const dayLogs = logs.filter((log) => {
        const d = new Date(log.created_at);
        return (
          d.getFullYear() === cellDate.getFullYear() &&
          d.getMonth() === cellDate.getMonth() &&
          d.getDate() === cellDate.getDate()
        );
      });

      // Xác định trạng thái tô màu cho ô lịch
      let cellClass = '';
      let heartIcon = '';
      if (dayLogs.some((l) => l.status === 'taken')) {
        cellClass = 'taken';
        heartIcon = '💖';
      } else if (dayLogs.some((l) => l.status === 'delayed')) {
        cellClass = 'delayed';
        heartIcon = '⏰';
      }

      cells.push(
        <div key={`day-${day}`} className={`calendar-cell ${cellClass}`}>
          <span className="day-num">{day}</span>
          {heartIcon && <span className="heart-indicator">{heartIcon}</span>}
        </div>
      );
    }

    return cells;
  };

  const formatDate = (dateStr) => {
    const d = new Date(dateStr);
    return d.toLocaleString('vi-VN', {
      hour: '2-digit',
      minute: '2-digit',
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  return (
    <div className="container">
      {/* Hiệu ứng bong bóng trái tim bay bay nền */}
      <span className="floating-heart" style={{ left: '5%', top: '80%', animationDelay: '0s' }}>🌸</span>
      <span className="floating-heart" style={{ left: '85%', top: '60%', animationDelay: '3s' }}>💖</span>
      <span className="floating-heart" style={{ left: '70%', top: '15%', animationDelay: '5s' }}>💕</span>
      
      <header>
        <h1>Quỳnh ơi uống thuốc nhé! 🌸</h1>
        <p>Bảng theo dõi và chăm sóc sức khỏe của Quỳnh iu 24/7</p>
      </header>

      <div className="dashboard-grid">
        {/* Cột trái: Thống kê & Form ghi chép thủ công */}
        <div className="sidebar">
          <div className="card streak-box" style={{ marginBottom: '24px' }}>
            <div className="streak-number">{streak}</div>
            <div className="streak-label">Ngày liên tục 💖</div>
            <p style={{ marginTop: '12px', fontSize: '0.9rem', opacity: 0.8 }}>
              {streak >= 7 ? 'Giỏi quá! Cứ thế phát huy em nhé 🥰' : 'Nhớ uống thuốc đúng giờ nha em iu!'}
            </p>
          </div>

          <div className="card" style={{ marginBottom: '24px' }}>
            <h2>Ghi chép bù ✍️</h2>
            <p style={{ fontSize: '0.85rem', opacity: 0.8, marginBottom: '15px' }}>
              Trường hợp bạn Quỳnh quên bấm nút trên Telegram, bạn có thể tự ghi nhận tại đây nhé!
            </p>
            <form onSubmit={handleManualSubmit} className="quick-action-form">
              <select
                value={formStatus}
                onChange={(e) => setFormStatus(e.target.value)}
              >
                <option value="taken">Đã uống 🌸</option>
                <option value="delayed">Hẹn tí nữa ⏰</option>
              </select>

              <div style={{ display: 'flex', gap: '8px' }}>
                <input
                  type="date"
                  value={formDate}
                  onChange={(e) => setFormDate(e.target.value)}
                  style={{ width: '60%' }}
                  required
                />
                <input
                  type="time"
                  value={formTime}
                  onChange={(e) => setFormTime(e.target.value)}
                  style={{ width: '40%' }}
                  required
                />
              </div>
              
              <input
                type="text"
                placeholder="Ghi chú (ví dụ: uống sau ăn...)"
                value={formNote}
                onChange={(e) => setFormNote(e.target.value)}
              />
              
              <button
                type="submit"
                disabled={isSubmitting}
                className="btn-pink"
              >
                {isSubmitting ? 'Đang lưu...' : 'Lưu lịch sử ✨'}
              </button>
            </form>
          </div>

          <div className="card">
            <h2>Kiểm thử Bot 🧪</h2>
            <p style={{ fontSize: '0.85rem', opacity: 0.8, marginBottom: '15px' }}>
              Nhấn vào nút dưới đây để bot gửi tin nhắn nhắc nhở lập tức lên Telegram nhằm kiểm tra nút bấm (không ghi vào DB).
            </p>
            <button
              onClick={handleSendTestReminder}
              className="btn-pink"
              style={{ background: '#7209b7', boxShadow: '0 4px 10px rgba(114, 9, 183, 0.3)' }}
            >
              Gửi tin nhắc ngay 🚀
            </button>
          </div>
        </div>

        {/* Cột phải: Lịch tháng & Lịch sử chi tiết */}
        <div className="main-content">
          <div className="card" style={{ marginBottom: '24px' }}>
            <div className="calendar-container">
              <div className="calendar-header">
                <h2 style={{ marginBottom: 0 }}>
                  Tháng {currentMonth.getMonth() + 1} / {currentMonth.getFullYear()}
                </h2>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <button onClick={handlePrevMonth}>&lt;</button>
                  <button onClick={handleNextMonth}>&gt;</button>
                </div>
              </div>

              <div className="calendar-days">
                <div>CN</div>
                <div>T2</div>
                <div>T3</div>
                <div>T4</div>
                <div>T5</div>
                <div>T6</div>
                <div>T7</div>
              </div>

              <div className="calendar-grid">
                {renderCalendar()}
              </div>
            </div>
          </div>

          <div className="card">
            <h2>Lịch sử chi tiết gần đây 🕒</h2>
            {isLoading ? (
              <p style={{ textAlign: 'center', padding: '20px' }}>Đang tải lịch sử...</p>
            ) : logs.length === 0 ? (
              <p style={{ textAlign: 'center', padding: '20px', opacity: 0.7 }}>Chưa có dữ liệu uống thuốc.</p>
            ) : (
              <div className="history-list">
                {logs.slice(0, 10).map((log) => (
                  <div
                    key={log.id}
                    className={`history-item ${log.status === 'delayed' ? 'delayed' : ''}`}
                  >
                    <div className="history-item-left">
                      <span className="history-status">
                        {log.status === 'taken' ? '🌸 Đã uống thuốc' : '⏰ Hẹn nhắc lại sau'}
                      </span>
                      {log.note && (
                        <span style={{ fontSize: '0.85rem', opacity: 0.8 }}>
                          Ghi chú: {log.note}
                        </span>
                      )}
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span className="history-time">
                        {formatDate(log.created_at)}
                      </span>
                      <button
                        onClick={() => handleDeleteLog(log.id)}
                        style={{
                          background: 'none',
                          border: 'none',
                          cursor: 'pointer',
                          fontSize: '1rem',
                          opacity: 0.6,
                          transition: 'opacity 0.2s',
                          padding: '4px'
                        }}
                        title="Xóa bản ghi này"
                        onMouseEnter={(e) => e.target.style.opacity = 1}
                        onMouseLeave={(e) => e.target.style.opacity = 0.6}
                      >
                        🗑️
                      </button>
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
