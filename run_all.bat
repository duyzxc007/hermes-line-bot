@echo off
echo =========================================
echo    Starting Hermes LINE Bot & Ngrok
echo =========================================

:: สั่งเปิดหน้าต่างใหม่สำหรับรัน Ngrok
echo [1/2] Starting Ngrok Tunnel in a new window...
start "Ngrok Tunnel" cmd /c ".\ngrok.exe http --domain=ace-lioness-instantly.ngrok-free.app 8000"

:: รอ 2 วินาทีให้ Ngrok รันเสร็จก่อน
timeout /t 2 >nul

:: รันบอทในหน้าต่างนี้เลย
echo [2/2] Starting Python Backend...
call uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause
