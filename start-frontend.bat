@echo off
cd /d "%~dp0frontend"
if not exist "node_modules" call npm install
if not exist ".env.local" copy .env.local.example .env.local
echo Starting KCET frontend on http://localhost:3000
echo API requests proxy to backend at http://127.0.0.1:8001
call npm run dev
