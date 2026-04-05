@echo off
echo Stopping existing Python processes gracefully...
taskkill /IM python.exe 2>nul
timeout /t 5 /nobreak >nul

echo Force killing any remaining Python processes...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul

echo Starting Flask server...
cd /d "%~dp0backend"
call venv\Scripts\activate
python app.py
