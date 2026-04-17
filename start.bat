@echo off
chcp 65001 >nul
title Deep Research Agent

:: Get the directory where this script resides
set "SCRIPT_DIR=%~dp0"
set "BACKEND_DIR=%SCRIPT_DIR%backend"
set "FRONTEND_DIR=%SCRIPT_DIR%frontend"

echo ========================================
echo   Deep Research Agent - Starting...
echo ========================================
echo.

:: --- Start Backend ---
echo [1/2] Starting Backend Server...
cd /d "%BACKEND_DIR%"
start "Backend" cmd /k "python -m uvicorn app.main:app --reload --port 8000"

:: Wait for backend to be ready
echo       Waiting for backend to start...
timeout /t 3 /nobreak >nul

:: --- Start Frontend ---
echo [2/2] Starting Frontend Dev Server...
cd /d "%FRONTEND_DIR%"
start "Frontend" cmd /k "npm run dev"

:: Wait for frontend to be ready
echo       Waiting for frontend to start...
timeout /t 4 /nobreak >nul

:: --- Open Browser ---
echo.
echo ========================================
echo   All services started!
echo   Opening browser at http://localhost:5173
echo ========================================
start http://localhost:5173

echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Press any key to exit this window...
pause >nul
