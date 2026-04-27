@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ==========================================
echo   APIMart Image Generator
echo ==========================================
echo.
python app.py
pause
