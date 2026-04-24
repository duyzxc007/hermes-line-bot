@echo off
chcp 65001 >nul
echo ===================================================
echo     Hermes Bot - Auto Setup ^& Run (For New PC)
echo ===================================================

echo [1/3] Checking Python installation...
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Python is not found on this computer!
    echo Please download and install Python 3.10 or newer from https://www.python.org/downloads/
    echo *** IMPORTANT: Check the box "Add Python to PATH" during installation. ***
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
echo   [SUCCESS] Libraries installed successfully! 
echo ===================================================
echo [3/3] Opening terminal windows for Ngrok and Bot...

:: Open separate windows to prevent auto-closing
start "Ngrok Tunnel" cmd /k ".\ngrok.exe http --domain=ace-lioness-instantly.ngrok-free.app 8000"
start "Hermes Bot" cmd /k "python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

exit
