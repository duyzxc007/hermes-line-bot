@echo off
chcp 65001 >nul
echo ===================================================
echo     Hermes Bot - Auto Setup ^& Run (For New PC)
echo ===================================================

echo [1/3] Checking Python installation...
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] ไม่พบโปรแกรม Python ในเครื่องนี้!
    echo กรุณาดาวน์โหลดและติดตั้ง Python 3.10 หรือใหม่กว่า จาก https://www.python.org/downloads/
    echo *** สำคัญมาก: ตอนติดตั้งหน้าแรกสุด ต้องติ๊กถูกที่ช่อง "Add Python to PATH" ด้วยนะครับ ***
    echo.
    pause
    exit /b
)

echo.
echo [2/3] Installing required libraries (This may take a while)...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo ===================================================
echo   [SUCCESS] ติดตั้งไลบรารีเสร็จสมบูรณ์! 
echo ===================================================
echo [3/3] กำลังเปิดหน้าต่างสำหรับรัน Ngrok และ Bot...

:: เปิดหน้าต่างแยกเพื่อไม่ให้ปิดตัวเอง
start "Ngrok Tunnel" cmd /k ".\ngrok.exe http --domain=ace-lioness-instantly.ngrok-free.app 8000"
start "Hermes Bot" cmd /k "python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

exit
