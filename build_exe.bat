@echo off
chcp 65001 >nul
echo ===================================================
echo     Hermes Bot - PyInstaller Build Script
echo ===================================================

echo [1/3] Checking dependencies...
python -m pip install pyinstaller

echo.
echo [2/3] Building the .exe file (This will take a LONG time)...
:: ใช้ pyinstaller คอมไพล์โปรแกรม
:: --onefile: รวมทุกอย่างเป็นไฟล์เดียว
:: --add-data: ฝังไฟล์ ngrok.exe และโฟลเดอร์ static เข้าไปด้วย
:: --hidden-import: บังคับดึงไลบรารีที่ชอบตกหล่น

python -m PyInstaller --name "HermesBot" --onefile ^
  --add-data "ngrok.exe;." ^
  --add-data "static;static" ^
  --hidden-import "chromadb" ^
  --hidden-import "sentence_transformers" ^
  --hidden-import "pydantic" ^
  --hidden-import "apscheduler" ^
  --hidden-import "duckduckgo_search" ^
  --hidden-import "uvicorn" ^
  main.py

echo.
echo ===================================================
echo [3/3] Build Complete!
echo ไฟล์บอทของคุณคือ HermesBot.exe อยู่ในโฟลเดอร์ "dist"
echo.
echo ** สำคัญมาก: ก่อนนำไปรันที่เครื่องอื่น **
echo ให้คัดลอกไฟล์ .env ไปวางไว้ที่โฟลเดอร์เดียวกับไฟล์ .exe ด้วยเสมอ
echo มิฉะนั้นบอทจะไม่มีรหัสผ่านในการทำงาน
echo ===================================================
pause
