@echo off
chcp 65001 >nul
echo ===================================================
echo     Hermes Bot - PyInstaller Build Script
echo ===================================================

echo [1/3] Checking dependencies...
python -m pip install pyinstaller

echo.
echo [2/3] Building the .exe file (This will take a LONG time)...
:: Use PyInstaller to compile
:: --onefile: bundle everything into a single executable
:: --add-data: embed ngrok.exe and static folder
:: --hidden-import: force include missing libraries

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
echo Your bot file is HermesBot.exe located in the "dist" folder.
echo.
echo ** VERY IMPORTANT: Before running on another computer **
echo Please copy the .env file to the same folder as the .exe file.
echo Otherwise, the bot will not have the required API keys.
echo ===================================================
pause
