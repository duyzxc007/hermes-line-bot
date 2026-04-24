@echo off
echo =========================================
echo    Starting Hermes LINE Bot & Ngrok
echo =========================================

:: เปิดหน้าต่างใหม่สำหรับรัน Ngrok (ใช้ /k เพื่อไม่ให้หน้าต่างปิดตัวเองถ้ามี Error จะได้เห็นว่าเกิดอะไรขึ้น)
start "Ngrok Tunnel" cmd /k ".\ngrok.exe http --domain=ace-lioness-instantly.ngrok-free.app 8000"

:: เปิดหน้าต่างใหม่สำหรับรัน Python Bot (ใช้ /k เช่นกัน)
start "Hermes Bot" cmd /k "uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

:: หน้าต่างหลักนี้หมดหน้าที่แล้ว ปิดตัวเองได้เลย
exit
