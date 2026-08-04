@echo off
title SFA - Frontend Server (Port 5173)
echo ============================================================
echo   STARTUP FUNDING ANALYTICS - Frontend (React/Vite)
echo   Running on: http://localhost:5173
echo ============================================================
echo.

set FRONTEND_DIR=%~dp0frontend
cd /d "%FRONTEND_DIR%"

where npm >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set NPM_CMD=npm
) else (
    if exist "C:\Program Files\nodejs\npm.cmd" (
        set NPM_CMD="C:\Program Files\nodejs\npm.cmd"
    ) else (
        set NPM_CMD=npm
    )
)

echo Starting React frontend...
call %NPM_CMD% run dev

pause
