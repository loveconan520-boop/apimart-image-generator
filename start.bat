@echo off
chcp 65001 >nul
echo 正在关闭占用 8080 端口的进程...

:: 查找并关闭占用 8080 端口的 Python 进程
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080 ^| findstr LISTENING') do (
    echo 关闭进程 PID: %%a
    taskkill /F /PID %%a 2>nul
)

echo.
echo 正在启动服务...
cd /d "C:\Users\zjj\.qclaw\workspace\apimart-image-generator-v2"
python app.py

pause
