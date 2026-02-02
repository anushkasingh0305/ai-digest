@echo off
REM Demo script: End-to-end AI Digest walkthrough (Windows PowerShell)
REM Usage: demo.ps1

setlocal enabledelayedexpansion

echo.
echo =========================================
echo AI Digest Demo - End-to-End Walkthrough
echo =========================================
echo.

REM Step 1: Check Python
echo [1/6] Checking Python environment...
python --version >nul 2>&1
if !errorlevel! neq 0 (
    echo ERROR: Python not found. Install Python 3.11+ and try again.
    exit /b 1
)
echo ^✓ Python is available
echo.

REM Step 2: Create virtualenv if needed
echo [2/6] Installing dependencies...
if not exist ".venv" (
    python -m venv .venv
    call .venv\Scripts\activate.bat
    pip install -q -r requirements.txt
) else (
    call .venv\Scripts\activate.bat
)
echo ^✓ Dependencies installed
echo.

REM Step 3: Copy .env.example if needed
echo [3/6] Setting up configuration...
if not exist ".env" (
    copy .env.example .env >nul
    echo   Created .env from .env.example
    echo   NOTE: Edit .env with your SMTP/Telegram credentials if desired
)
echo ^✓ Configuration ready
echo.

REM Step 4: Run tests
echo [4/6] Running unit tests...
python -m pytest tests/ -q --tb=short
if !errorlevel! neq 0 (
    echo ERROR: Tests failed
    exit /b 1
)
echo ^✓ All tests passed
echo.

REM Step 5: Run pipeline
echo [5/6] Running AI Digest pipeline...
echo   Ingesting items from placeholder adapter...
python -m src.cli.main
echo ^✓ Pipeline completed
echo.

REM Step 6: Show results
echo [6/6] Pipeline output:
if exist "out\digest.json" (
    echo   Digest saved to: out/digest.json
    echo   Contents:
    python -c "import json; data = json.load(open('out/digest.json')); print('    - Items:', len(data.get('items', []))); [print(f'      * {i.get(\"title\", \"(no title)\")}') for i in data.get('items', [])]"
) else (
    echo   (No output file found)
)
echo.

echo =========================================
echo Demo Complete!
echo =========================================
echo.
echo Next steps:
echo 1. Configure .env with real credentials (SMTP, Telegram, etc.)
echo 2. Run with delivery: python -m src.cli.main --deliver
echo 3. Start Docker stack: docker-compose up --build -d
echo 4. Visit Grafana: http://localhost:3000
echo.
echo For more info, see:
echo   - README.md — Quick start
echo   - DEPLOYMENT.md — Full setup guide
echo   - DELIVERABLES.md — Features ^& roadmap
echo.

pause
