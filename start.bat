@echo off
setlocal
title AI Job Application Copilot - Launcher

echo ================================================================
echo       AI Job Application Copilot - Khoi Dong He Thong
echo ================================================================
echo.

pushd "%~dp0"
set "ROOT_DIR=%CD%"
popd

set "BACKEND_DIR=%ROOT_DIR%\backend"
set "FRONTEND_DIR=%ROOT_DIR%\frontend"

REM 1. Kiem tra Python Virtual Environment
if not exist "%BACKEND_DIR%\venv\Scripts\python.exe" (
    echo [!] Chua tim thay venv trong backend.
    echo [*] Dang khoi tao venv va cai dat dependencies...
    python -m venv "%BACKEND_DIR%\venv"
    call "%BACKEND_DIR%\venv\Scripts\activate"
    pip install -r "%BACKEND_DIR%\requirements.txt"
)

REM 2. Kiem tra va nhac cau hinh API Key
call "%BACKEND_DIR%\venv\Scripts\python.exe" "%BACKEND_DIR%\setup_env.py"

echo.
echo ================================================================
echo [*] Buoc 1/3: Khoi dong Backend (FastAPI tai cong 8000)...
echo ================================================================
start "AI Copilot - Backend (FastAPI :8000)" cmd /k "title Backend (FastAPI :8000) && cd /d %BACKEND_DIR% && call venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"

echo.
echo ================================================================
echo [*] Buoc 2/3: Khoi dong Frontend (Next.js tai cong 3000)...
echo ================================================================
start "AI Copilot - Frontend (Next.js :3000)" cmd /k "title Frontend (Next.js :3000) && cd /d %FRONTEND_DIR% && npm run dev"

echo.
echo ================================================================
echo [*] Buoc 3/3: Dang cho dich vu san sang (khoang 5 giay)...
echo ================================================================
timeout /t 5 /nobreak >nul

echo [*] Dang mo trinh duyet toi http://localhost:3000 ...
start http://localhost:3000

echo.
echo ================================================================
echo   [OK] HE THONG DA KHOI CHAY THANH CONG!
echo.
echo   - Giao dien nguoi dung: http://localhost:3000
echo   - Tai lieu API Backend: http://localhost:8000/docs
echo.
echo   De dung ung dung:
echo   1. Dong 2 cua so Backend va Frontend
echo   2. Hoac chay file stop.bat
echo ================================================================
echo.
pause
