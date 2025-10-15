@echo off
echo ========================================
echo Starting Fortes Eduction Application
echo ========================================
echo.
echo This will open 2 terminal windows:
echo   1. Backend (Python/FastAPI) on port 8000
echo   2. Frontend (Next.js) on port 3000/3001
echo.
echo Press any key to continue...
pause >nul

echo.
echo Starting Backend...
start "Fortes Backend" cmd /k "%~dp0start_backend.bat"

echo Waiting 5 seconds for backend to initialize...
timeout /t 5 /nobreak >nul

echo Starting Frontend...
start "Fortes Frontend" cmd /k "%~dp0start_frontend.bat"

echo.
echo ========================================
echo Application Starting!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo You can close this window.
echo The app is running in the 2 other windows.
echo.
pause

