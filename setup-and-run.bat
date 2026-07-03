@echo off
REM KCET 2026 Portal - one-shot setup then open dev servers
echo.
echo ======================================
echo  KCET 2026 Portal - Full Setup
echo ======================================
echo.

cd /d "%~dp0"

if not exist "backend\.env" copy backend\.env.example backend\.env
if not exist "frontend\.env.local" copy frontend\.env.local.example frontend\.env.local

if not exist "backend\venv" (
    echo [1/5] Creating Python venv...
    cd backend
    python -m venv venv
    cd ..
) else (
    echo [1/5] Python venv already exists
)

echo [2/5] Installing backend dependencies...
call backend\venv\Scripts\activate.bat
pip install -r backend\requirements.txt

echo [3/5] Installing frontend dependencies...
cd frontend
call npm install
cd ..

echo [4/5] Building college master list (2026-27 codewise)...
python parse_college_list_pdf.py --fallback-only
if exist "LIST OF COLLEGES DURING 2026-27 (CODEWISE)*.pdf" (
    echo Found official college list PDF — re-parsing...
    python parse_college_list_pdf.py
)

echo [5/5] Importing cutoff data (optional, may take a minute)...
cd backend
python run_import.py
cd ..

echo.
echo Setup complete. Starting servers...
echo   Frontend: http://localhost:3000
echo   Backend:  http://127.0.0.1:8001
echo   IMPORTANT: Start backend FIRST, wait for "Uvicorn running", then use the app.
echo.

start "KCET Backend" cmd /k "%~dp0start-backend.bat"
echo Waiting for backend to start...
timeout /t 8 /nobreak >nul

curl.exe -s http://127.0.0.1:8001/api/health >nul 2>&1
if errorlevel 1 (
    echo WARNING: Backend not responding yet. Check the KCET Backend window for errors.
    echo First startup can take 30-60 seconds while cutoff data loads.
) else (
    echo Backend is healthy.
)

start "KCET Frontend" cmd /k "%~dp0start-frontend.bat"

echo.
echo Two terminal windows opened. Press any key to close this window.
pause >nul
