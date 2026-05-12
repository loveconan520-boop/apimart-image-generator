@echo off
taskkill /F /IM python.exe 2>nul
taskkill /F /IM python3.exe 2>nul
taskkill /F /IM python3.11.exe 2>nul
timeout /t 1 /nobreak >nul
python app.py
