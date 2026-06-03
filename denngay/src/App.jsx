import React, { useState, useEffect, useMemo } from 'react';

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

// Giải mã payload từ Google ID Token JWT
const decodeJwt = (token) => {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function(c) {
      return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    return JSON.parse(jsonPayload);
  } catch (e) {
    return null;
  }
};

// Định dạng ngày sang YYYY-MM-DD theo múi giờ địa phương
const formatDateISO = (date) => {
  const d = new Date(date);
  let month = '' + (d.getMonth() + 1);
  let day = '' + d.getDate();
  const year = d.getFullYear();

  if (month.length < 2) month = '0' + month;
  if (day.length < 2) day = '0' + day;

  return [year, month, day].join('-');
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

  // Các State cho Stardust và Google OAuth
  const [stardustLogs, setStardustLogs] = useState(null);
  const [googleUser, setGoogleUser] = useState(null);
  const [rowndToken, setRowndToken] = useState(null);
  const [googleClientId, setGoogleClientId] = useState(
    localStorage.getItem('google_client_id') || '900415098360-ritfis4563e74sluvre9nsmhi2oa4uf0.apps.googleusercontent.com'
  );
  const [isSyncingStardust, setIsSyncingStardust] = useState(false);
  const [showClientIdInput, setShowClientIdInput] = useState(false);

  // Tải session đã lưu của Stardust khi khởi chạy
  useEffect(() => {
    // Tự động dọn dẹp Client ID có lỗi chính tả trong localStorage của người dùng
    const savedId = localStorage.getItem('google_client_id');
    if (savedId && (savedId.includes('ritfls') || savedId.includes('slvvre'))) {
      localStorage.removeItem('google_client_id');
      setGoogleClientId('900415098360-ritfis4563e74sluvre9nsmhi2oa4uf0.apps.googleusercontent.com');
    }

    const rawSession = localStorage.getItem('stardust_session');
    if (rawSession) {
      try {
        const session = JSON.parse(rawSession);
        if (session.googleUser) setGoogleUser(session.googleUser);
        if (session.rowndToken) {
          setRowndToken(session.rowndToken);
          fetchStardustLogs(session.rowndToken);
        }
      } catch (e) {
        console.error('Không thể load session Stardust:', e);
      }
    }
  }, []);

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

  // Các hàm chức năng cho Stardust
  const fetchStardustLogs = async (token) => {
    setIsSyncingStardust(true);
    try {
      const res = await fetch(`${API_URL}/api/extract`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ access_token: token })
      });
      const data = await res.json();
      if (res.ok) {
        setStardustLogs(data);
      } else {
        throw new Error(data.error || 'Failed to extract logs');
      }
    } catch (err) {
      console.error(err);
      alert('Không thể tải dữ liệu Stardust. Vui lòng kiểm tra lại token hoặc đăng nhập lại.');
      handleStardustLogout();
    } finally {
      setIsSyncingStardust(false);
    }
  };

  const handleGoogleIdToken = async (idToken) => {
    const payload = decodeJwt(idToken);
    let user = null;
    if (payload) {
      user = {
        name: payload.name,
        email: payload.email,
        picture: payload.picture
      };
      setGoogleUser(user);
    }

    setIsSyncingStardust(true);
    try {
      const authRes = await fetch(`${API_URL}/api/authenticate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id_token: idToken })
      });

      const authData = await authRes.json();
      if (authRes.ok && authData.access_token) {
        setRowndToken(authData.access_token);
        localStorage.setItem('stardust_session', JSON.stringify({
          googleUser: user,
          rowndToken: authData.access_token
        }));
        await fetchStardustLogs(authData.access_token);
      } else {
        throw new Error(authData.error || 'Authentication failed');
      }
    } catch (err) {
      console.error(err);
      alert('Đăng nhập Stardust thất bại: ' + err.message);
    } finally {
      setIsSyncingStardust(false);
    }
  };

  const loginWithGooglePopup = () => {
    const client_id = googleClientId.trim();
    if (!client_id) {
      alert('Vui lòng cấu hình Google Client ID trước.');
      return;
    }
    const redirect_uri = window.location.origin;
    const scope = 'openid email profile';
    const nonce = 'stardust_' + Math.random().toString(36).substring(2);
    const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${client_id}&redirect_uri=${encodeURIComponent(redirect_uri)}&response_type=id_token&scope=${encodeURIComponent(scope)}&nonce=${nonce}`;
    
    const width = 500;
    const height = 650;
    const left = (window.screen.width - width) / 2;
    const top = (window.screen.height - height) / 2;
    
    const popup = window.open(
      authUrl,
      'GoogleLoginPopup',
      `width=${width},height=${height},left=${left},top=${top},status=no,resizable=yes`
    );
    
    if (!popup) {
      alert('Trình duyệt đã chặn cửa sổ Popup. Vui lòng cho phép popup để đăng nhập bằng Google.');
      return;
    }
    
    const pollTimer = window.setInterval(() => {
      try {
        if (popup.closed) {
          window.clearInterval(pollTimer);
          return;
        }
        
        if (popup.location.origin === window.location.origin) {
          const hash = popup.location.hash;
          if (hash) {
            window.clearInterval(pollTimer);
            popup.close();
            
            const params = new URLSearchParams(hash.substring(1));
            const idToken = params.get('id_token');
            if (idToken) {
              handleGoogleIdToken(idToken);
            }
          }
        }
      } catch (e) {
        // Bỏ qua lỗi CORS khi ở domain Google
      }
    }, 500);
  };

  const handleStardustLogout = () => {
    localStorage.removeItem('stardust_session');
    setGoogleUser(null);
    setRowndToken(null);
    setStardustLogs(null);
  };

  const handleSaveClientId = (newId) => {
    localStorage.setItem('google_client_id', newId);
    setGoogleClientId(newId);
    alert('Đã lưu Google Client ID thành công! 🌸');
    setShowClientIdInput(false);
  };

  // Map dữ liệu để tra cứu nhanh theo ngày YYYY-MM-DD
  const stardustLogsMap = useMemo(() => {
    if (!stardustLogs) return {};
    const list = Array.isArray(stardustLogs)
      ? stardustLogs
      : (stardustLogs.logs || stardustLogs.data || []);
    
    const map = {};
    list.forEach((log) => {
      if (log.date) {
        map[log.date] = log;
      }
    });
    return map;
  }, [stardustLogs]);

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

      // Xác định trạng thái từ Stardust (hành kinh / rụng trứng)
      const dateStr = formatDateISO(cellDate);
      const dayLog = stardustLogsMap[dateStr];
      let hasPeriod = false;
      let hasOvulation = false;

      if (dayLog) {
        hasPeriod = dayLog.period === true || 
                    dayLog.bleeding === true || 
                    (dayLog.flow && dayLog.flow !== 'none') || 
                    (dayLog.fields && (dayLog.fields.period || dayLog.fields.bleeding));
                    
        hasOvulation = dayLog.ovulation === true || 
                       (dayLog.fields && dayLog.fields.ovulation);
      }

      const classes = [
        'calendar-cell',
        cellClass,
        hasPeriod ? 'has-period' : '',
        hasOvulation ? 'has-ovulation' : ''
      ].filter(Boolean).join(' ');

      cells.push(
        <div key={`day-${day}`} className={classes}>
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

          {/* Đồng bộ Stardust */}
          <div className="card stardust-sync-card" style={{ marginBottom: '24px' }}>
            <h2>Đồng bộ Stardust 🩸</h2>
            {isSyncingStardust ? (
              <p style={{ textAlign: 'center', padding: '10px' }}>Đang đồng bộ dữ liệu...</p>
            ) : !googleUser ? (
              <div className="stardust-sync-form">
                <p style={{ fontSize: '0.85rem', opacity: 0.8 }}>
                  Kết nối với tài khoản Stardust của bạn qua Google để hiển thị ngày hành kinh và rụng trứng trên lịch.
                </p>
                
                <button
                  type="button"
                  onClick={loginWithGooglePopup}
                  className="btn-pink"
                  style={{ width: '100%' }}
                >
                  Đăng nhập Google 🔑
                </button>

                <div style={{ marginTop: '8px', textAlign: 'center' }}>
                  <a
                    href="#configure"
                    onClick={(e) => {
                      e.preventDefault();
                      setShowClientIdInput(!showClientIdInput);
                    }}
                    style={{ fontSize: '0.8rem', color: 'var(--pink-hover)', textDecoration: 'underline', cursor: 'pointer' }}
                  >
                    {showClientIdInput ? 'Ẩn cấu hình Client ID' : 'Cấu hình Google Client ID'}
                  </a>
                </div>

                {showClientIdInput && (
                  <div style={{ marginTop: '12px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <label style={{ fontSize: '0.8rem', fontWeight: 600 }}>Google Client ID:</label>
                    <input
                      type="text"
                      value={googleClientId}
                      onChange={(e) => setGoogleClientId(e.target.value)}
                      placeholder="Nhập Google Client ID của bạn..."
                      style={{ fontSize: '0.8rem', padding: '8px' }}
                    />
                    <button
                      type="button"
                      onClick={() => handleSaveClientId(googleClientId)}
                      className="btn-pink"
                      style={{ fontSize: '0.85rem', padding: '6px 12px', background: '#7209b7' }}
                    >
                      Lưu ID
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '15px' }}>
                  <img
                    src={googleUser.picture || 'https://lh3.googleusercontent.com/a/default-user'}
                    alt="Avatar"
                    style={{ width: '40px', height: '40px', borderRadius: '50%', border: '2px solid var(--pink-pastel)' }}
                  />
                  <div style={{ minWidth: 0 }}>
                    <div style={{ fontWeight: 600, fontSize: '0.95rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {googleUser.name}
                    </div>
                    <div style={{ fontSize: '0.8rem', opacity: 0.7, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {googleUser.email}
                    </div>
                  </div>
                </div>

                {/* Thống kê Stardust */}
                {(() => {
                  const list = Array.isArray(stardustLogs) ? stardustLogs : (stardustLogs?.logs || stardustLogs?.data || []);
                  
                  // Tính chu kỳ / kinh nguyệt trung bình
                  const periodDays = list.filter(item => {
                    return item.period === true || 
                           item.bleeding === true || 
                           (item.flow && item.flow !== 'none') || 
                           (item.symptoms && item.symptoms.includes('bleeding')) ||
                           (item.fields && (item.fields.period || item.fields.bleeding));
                  }).map(item => item.date).sort();

                  let avgPeriodLength = '--';
                  let avgCycleLength = '--';

                  if (periodDays.length > 0) {
                    const periods = [];
                    let currentPeriod = [new Date(periodDays[0])];

                    for (let i = 1; i < periodDays.length; i++) {
                      const prevDate = new Date(periodDays[i - 1]);
                      const currDate = new Date(periodDays[i]);
                      const diffTime = Math.abs(currDate - prevDate);
                      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

                      if (diffDays <= 2) {
                        currentPeriod.push(currDate);
                      } else {
                        periods.push(currentPeriod);
                        currentPeriod = [currDate];
                      }
                    }
                    periods.push(currentPeriod);

                    const totalPeriodDays = periods.reduce((sum, p) => sum + p.length, 0);
                    avgPeriodLength = `${Math.round(totalPeriodDays / periods.length)} ngày`;

                    if (periods.length > 1) {
                      let cycleDiffSum = 0;
                      for (let i = 1; i < periods.length; i++) {
                        const prevStart = periods[i - 1][0];
                        const currStart = periods[i][0];
                        const diffTime = Math.abs(currStart - prevStart);
                        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                        cycleDiffSum += diffDays;
                      }
                      avgCycleLength = `${Math.round(cycleDiffSum / (periods.length - 1))} ngày`;
                    } else {
                      avgCycleLength = '28 ngày';
                    }
                  }

                  return (
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '15px' }}>
                      <div style={{ background: '#fff', padding: '10px', borderRadius: '8px', border: '1px solid var(--pink-pastel)', textAlign: 'center' }}>
                        <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: 'var(--pink-primary)' }}>{avgPeriodLength}</div>
                        <div style={{ fontSize: '0.75rem', opacity: 0.8 }}>Kỳ kinh TB</div>
                      </div>
                      <div style={{ background: '#fff', padding: '10px', borderRadius: '8px', border: '1px solid var(--pink-pastel)', textAlign: 'center' }}>
                        <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: 'var(--pink-primary)' }}>{avgCycleLength}</div>
                        <div style={{ fontSize: '0.75rem', opacity: 0.8 }}>Chu kỳ TB</div>
                      </div>
                    </div>
                  );
                })()}

                <div style={{ display: 'flex', gap: '8px' }}>
                  <button
                    type="button"
                    onClick={() => fetchStardustLogs(rowndToken)}
                    className="btn-pink btn-blue"
                    style={{ flex: 1, fontSize: '0.9rem', padding: '10px' }}
                  >
                    Đồng bộ lại 🔄
                  </button>
                  <button
                    type="button"
                    onClick={handleStardustLogout}
                    className="btn-pink"
                    style={{ flex: 1, fontSize: '0.9rem', padding: '10px', background: '#ccc', color: '#333', boxShadow: 'none' }}
                  >
                    Đăng xuất 🚪
                  </button>
                </div>
              </div>
            )}
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

              {googleUser && (
                <div className="calendar-legend-stardust">
                  <div className="legend-item">
                    <span>🔴</span>
                    <span>Ngày hành kinh</span>
                  </div>
                  <div className="legend-item">
                    <span>🔵</span>
                    <span>Ngày rụng trứng</span>
                  </div>
                </div>
              )}
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
