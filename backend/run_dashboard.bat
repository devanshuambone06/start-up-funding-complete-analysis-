@echo off
echo Starting Ledger - Startup Funding Intelligence Dashboard...
cd /d "%~dp0"
"..\\.venv\\Scripts\\streamlit.exe" run dashboard/app.py
pause
