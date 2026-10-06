@echo off
chcp 65001 >nul
title AI Job Application Copilot - Launcher

echo ================================================================
echo       AI Job Application Copilot - Khởi Động Hệ Thống
echo ================================================================
echo.

set "ROOT_DIR=%~dp0"
:: Remove trailing backslash if present
if "%ROOT_DIR:~-1%"=="\" set "ROOT_DIR=%ROOT_DIR:~0,-1%"

set "BACKEND_DIR=%ROOT_DIR%\backend"
set "FRONTEND_DIR=%ROOT_DIR%\frontend"

:: 1. Kiểm tra Python Virtual Environment
if not exist "%BACKEND_DIR%\venv\Scripts\python.exe" (
    echo [!] Chưa tìm thấy môi trường ảo venv trong backend.
    echo [*] Đang khởi tạo venv và cài đặt dependencies...
    python -m venv "%BACKEND_DIR%\venv"
    call "%BACKEND_DIR%\venv\Scripts\activate"
    pip install -r "%BACKEND_DIR%\requirements.txt"
)

:: 2. Kiểm tra và nhắc cấu hình API Key
call "%BACKEND_DIR%\venv\Scripts\python.exe" "%BACKEND_DIR%\setup_env.py"

echo.
echo ================================================================
echo [*] Bước 1/3: Khởi động Backend (FastAPI tại cổng 8000)...
echo ================================================================
start "AI Copilot - Backend (FastAPI :8000)" cmd /k "title Backend (FastAPI :8000) && cd /d %BACKEND_DIR% && call venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"

echo.
echo ================================================================
echo [*] Bước 2/3: Khởi động Frontend (Next.js tại cổng 3000)...
echo ================================================================
start "AI Copilot - Frontend (Next.js :3000)" cmd /k "title Frontend (Next.js :3000) && cd /d %FRONTEND_DIR% && npm run dev"

echo.
echo ================================================================
echo [*] Bước 3/3: Đang chờ dịch vụ sẵn sàng (khoảng 5 giây)...
echo ================================================================
timeout /t 5 /nobreak >nul

echo [*] Đang mở trình duyệt tới http://localhost:3000 ...
start http://localhost:3000

echo.
echo ================================================================
echo   ✓ HỆ THỐNG ĐÃ KHỞI CHẠY THÀNH CÔNG!
echo.
echo   - Giao diện người dùng: http://localhost:3000
echo   - Tài liệu API Backend: http://localhost:8000/docs
echo.
echo   Để dừng ứng dụng, bạn có thể:
echo   1. Đóng 2 cửa sổ Backend và Frontend
echo   2. Hoặc chạy file stop.bat
echo ================================================================
echo.
pause
