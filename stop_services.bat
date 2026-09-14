@echo off
chcp 65001 >nul
title Dừng toàn bộ Vortex Microservices
echo =================================================================
echo   Đang tắt toàn bộ microservices trên cổng 8000, 8001, 8002...
echo =================================================================
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 8000,8001,8002 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"
echo.
echo [✓] Đã tắt sạch toàn bộ các tiến trình microservices!
echo.
pause
