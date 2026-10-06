@echo off
chcp 65001 >nul
title AI Job Application Copilot - Stop Services

echo ================================================================
echo       AI Job Application Copilot - Dừng Dịch Vụ
echo ================================================================
echo.

echo [*] Đang giải phóng cổng 8000 (Backend)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo [*] Đang giải phóng cổng 3000 (Frontend)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo [✓] Đã dừng toàn bộ dịch vụ Backend và Frontend thành công!
echo.
timeout /t 3 /nobreak >nul
