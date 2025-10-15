@echo off
echo ========================================
echo Stopping Fortes Eduction Application
echo ========================================
echo.
echo Stopping all Python processes (Backend)...
taskkill /F /IM python.exe >nul 2>&1
if %errorlevel%==0 (
    echo Backend stopped successfully.
) else (
    echo No backend processes found.
)

echo.
echo Stopping all Node processes (Frontend)...
taskkill /F /IM node.exe >nul 2>&1
if %errorlevel%==0 (
    echo Frontend stopped successfully.
) else (
    echo No frontend processes found.
)

echo.
echo ========================================
echo Application Stopped
echo ========================================
echo.
pause

