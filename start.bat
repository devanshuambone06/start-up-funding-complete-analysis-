@echo off
echo ============================================================
echo  STARTUP FUNDING ANALYTICS - Full-Stack Local Launcher
echo ============================================================
echo.

set PROJECT_ROOT=%~dp0

echo [1/2] Starting FastAPI Backend (port 8000)...
start "SFA Backend" cmd /k ""%PROJECT_ROOT%start_backend.bat""

ping 127.0.0.1 -n 5 > nul

echo [2/2] Starting React Frontend (port 5173)...
start "SFA Frontend" cmd /k ""%PROJECT_ROOT%start_frontend.bat""

echo.
echo ============================================================
echo  Dono servers start ho rahe hain. Browser mein kholein:
echo.
echo   App:      http://localhost:5173
echo   API Docs: http://localhost:8000/docs
echo   Health:   http://localhost:8000/api/health
echo ============================================================
echo.

echo Frontend ready hone ka wait kar raha hai...
ping 127.0.0.1 -n 8 > nul
start http://localhost:5173
