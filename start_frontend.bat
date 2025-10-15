@echo off
cd frontend
echo ========================================
echo Starting Fortes Education Frontend
echo ========================================
echo.
echo Port: 3000 (or 3001 if 3000 is busy)
echo Backend API: http://localhost:8000
echo.

set NEXT_PUBLIC_API_URL=http://localhost:8000

npm run dev

