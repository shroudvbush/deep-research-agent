@echo off
chcp 65001 >nul 2>&1
title Deep Research Agent
setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "PORT=3000"
set "BACKEND_PORT=8000"

echo ========================================
echo    Deep Research Agent - Launcher
echo ========================================
echo.

echo [1/4] Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo       Python not found! Please install Python 3.8+
    echo       Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

if not exist "%SCRIPT_DIR%venv" (
    echo       Creating virtual environment...
    python -m venv "%SCRIPT_DIR%venv"
    if errorlevel 1 (
        echo       Failed to create venv.
        pause
        exit /b 1
    )
)

if not exist "%SCRIPT_DIR%venv\.installed" (
    echo       Installing Python dependencies...
    call "%SCRIPT_DIR%venv\Scripts\activate.bat"
    pip install -r "%SCRIPT_DIR%requirements.txt" -q
    if errorlevel 1 (
        echo       pip install failed, retrying...
        pip install -r "%SCRIPT_DIR%requirements.txt"
    )
    echo.> "%SCRIPT_DIR%venv\.installed"
) else (
    echo       Python dependencies ready.
)

if not exist "%SCRIPT_DIR%.env" (
    if exist "%SCRIPT_DIR%.env.example" (
        echo       Copying .env.example to .env ...
        copy "%SCRIPT_DIR%.env.example" "%SCRIPT_DIR%.env" >nul
        echo       IMPORTANT: Please edit .env and add your API key!
    )
)

echo [2/4] Checking Node.js environment...
node --version >nul 2>&1
if errorlevel 1 (
    echo       Node.js not found! Please install Node.js 18+
    echo       Download: https://nodejs.org/
    pause
    exit /b 1
)

if not exist "%SCRIPT_DIR%node_modules\vite" (
    echo       Installing frontend dependencies...
    cd /d "%SCRIPT_DIR%"
    call npm install
    if errorlevel 1 (
        echo       npm install failed!
        pause
        exit /b 1
    )
) else (
    echo       Frontend dependencies ready.
)

echo [3/4] Starting Backend Server...
start "Deep Research - Backend" cmd /k "set PYTHONIOENCODING=utf-8 & call "%SCRIPT_DIR%venv\Scripts\activate.bat" & cd /d "%SCRIPT_DIR%" & python -m uvicorn app.main:app --host 0.0.0.0 --port %BACKEND_PORT%"

echo       Waiting for backend...
timeout /t 3 /nobreak >nul

echo [4/4] Starting Frontend Dev Server...
cd /d "%SCRIPT_DIR%"
start "Deep Research - Frontend" cmd /k "cd /d "%SCRIPT_DIR%" & npx vite --port %PORT% --open"

echo.
echo ========================================
echo    All services started!
echo    Backend:  http://localhost:%BACKEND_PORT%
echo    Frontend: http://localhost:%PORT%
echo ========================================
echo.
echo    Close the Backend/Frontend windows to stop.
echo.
pause
