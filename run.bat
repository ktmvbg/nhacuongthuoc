@echo off
title nhacuongthuoc Dev Runner
echo ===================================================
echo   Dang khoi dong web app nhacuongthuoc (Offline Mode)
echo ===================================================
echo.
echo 1. Di chuyen vao thu muc frontend (denngay)...
cd denngay
echo.
echo 2. Dang kiem tra va cai dat dependencies (npm install)...
call npm install
echo.
echo 3. Dang build ung dung React bang Vite...
call npm run build
echo.
echo 4. Dang khoi dong server Express tren cong 3000...
start cmd /c "title nhacuongthuoc Local Server && npm start"
echo.
echo 5. Doi server khoi dong trong 2 giay...
timeout /t 2 >nul
echo.
echo 6. Dang mo giao dien website tren trinh duyet mac dinh...
start http://localhost:3000/
echo.
echo ===================================================
echo   KHOI DONG THANH CONG!
echo   - Website dang chay tai: http://localhost:3000/
echo   - Server dang chay o mot cua so cmd khac.
echo   - Ban co the dong cua so nay bat ky luc nao.
echo ===================================================
echo.
pause
