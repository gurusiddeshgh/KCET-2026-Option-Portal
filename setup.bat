@echo off
REM KCET 2026 Portal - Setup Script for Windows
REM This script automates the setup process for both backend and frontend

setlocal enabledelayedexpansion

echo.
echo ======================================
echo 🚀 KCET 2026 Portal Setup Script
echo ======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed
    exit /b 1
)

echo ✅ All prerequisites found
echo.

REM Backend Setup
echo Setting up Backend...
cd backend

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
    echo ⚠️  Please edit .env with your database credentials
)

cd ..
echo ✅ Backend setup complete
echo.

REM Frontend Setup
echo Setting up Frontend...
cd frontend

echo Installing dependencies...
call npm install

if not exist ".env.local" (
    echo Creating .env.local file...
    copy .env.local.example .env.local
)

cd ..
echo ✅ Frontend setup complete
echo.

echo 🎉 Setup Complete!
echo.
echo Next steps:
echo 1. Edit backend\.env with your database credentials
echo 2. Make sure PostgreSQL is running
echo 3. Run: cd backend ^&^& venv\Scripts\activate.bat ^&^& python main.py
echo 4. In another terminal: cd frontend ^&^& npm run dev
echo 5. Visit http://localhost:3000
echo.
pause
