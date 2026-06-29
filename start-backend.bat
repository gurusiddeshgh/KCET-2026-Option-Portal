@echo off
cd /d "%~dp0backend"
if not exist "venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)
if not exist ".env" copy .env.example .env
echo Starting KCET backend on http://127.0.0.1:8001
echo API docs: http://127.0.0.1:8001/docs
python main.py
