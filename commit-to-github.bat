@echo off
cd /d "%~dp0"

echo Staging changes...
git add ^
  backend/algorithms.py ^
  backend/database.py ^
  backend/main.py ^
  backend/data_loader.py ^
  backend/.env.example ^
  frontend/next.config.js ^
  frontend/.env.local.example ^
  frontend/src/services/api.ts ^
  frontend/src/components/StudentProfileForm.tsx ^
  frontend/src/app/predictor/page.tsx ^
  frontend/src/store/optionEntry.ts ^
  setup.bat ^
  setup-and-run.bat ^
  start-backend.bat ^
  start-frontend.bat ^
  tasks.json ^
  commit-to-github.bat

echo.
echo Staged files:
git diff --cached --stat

echo.
git commit -m "Fix portal setup, API connectivity, and prediction null-cutoff handling." -m "Use SQLite by default, proxy API through Next.js, and handle missing round cutoffs so predictions no longer 500."

if errorlevel 1 (
    echo Commit failed — maybe nothing to commit or a hook rejected it.
    pause
    exit /b 1
)

echo.
echo Pushing to GitHub...
git push origin main

if errorlevel 1 (
    echo Push failed — check GitHub login: gh auth login
    pause
    exit /b 1
)

echo.
echo Done!
git log -1 --oneline
pause
