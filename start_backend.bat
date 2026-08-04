@echo off
title SFA - Backend Server (Port 8000)
echo ============================================================
echo   STARTUP FUNDING ANALYTICS - Backend (FastAPI)
echo   Running on: http://localhost:8000
echo ============================================================
echo.

set PROJECT_ROOT=%~dp0
set BACKEND_DIR=%PROJECT_ROOT%backend

if exist "%PROJECT_ROOT%.venv\Scripts\python.exe" (
    set PYTHON_CMD="%PROJECT_ROOT%.venv\Scripts\python.exe"
) else if exist "%PROJECT_ROOT%..\Startup_Funding_Project_Production\.venv\Scripts\python.exe" (
    set PYTHON_CMD="%PROJECT_ROOT%..\Startup_Funding_Project_Production\.venv\Scripts\python.exe"
) else (
    set PYTHON_CMD=python
)

set PYTHONPATH=%BACKEND_DIR%
cd /d "%BACKEND_DIR%"

echo Starting FastAPI backend...
%PYTHON_CMD% -m uvicorn api.main:app --reload --port 8000 --host 0.0.0.0

pause
