@echo off
echo Starting Ngrok Tunnel with Static Domain...

.\ngrok.exe http --domain=ace-lioness-instantly.ngrok-free.app 8000

pause
