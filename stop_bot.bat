@echo off
echo Stopping Hermes Bot and Ngrok...

taskkill /F /IM ngrok.exe
taskkill /F /IM python.exe

echo All background processes have been stopped.
pause
