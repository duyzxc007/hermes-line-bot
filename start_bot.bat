@echo off
echo Starting Hermes LINE Bot Backend...
call uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
