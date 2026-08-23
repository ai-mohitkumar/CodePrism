@echo off
echo Starting CodePrism FastAPI Backend on http://127.0.0.1:8080 ...
cd /d "%~dp0backend"
call venv\Scripts\activate
uvicorn app.main:app --host 127.0.0.1 --port 8080 --reload
pause
