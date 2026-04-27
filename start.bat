@echo off
chcp 65001 >nul
echo ==========================================
echo   APIMart Image Generator v2
echo ==========================================
echo.
echo 正在启动代理服务器...
echo.
python proxy_server.py
pause
