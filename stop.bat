@echo off
setlocal
title AI Job Application Copilot - Stop Services

echo ================================================================
echo       AI Job Application Copilot - Dung Dich Vu
echo ================================================================
echo.

echo [*] Dang giai phong cong 8000 (Backend)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo [*] Dang giai phong cong 3000 (Frontend)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo [OK] Da dung toan bo dich vu Backend va Frontend!
echo.
timeout /t 3 /nobreak >nul
