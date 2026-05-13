@echo off
title AIR — AI Intermediate Representation Server
color 0A

echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║   AIR — AI Intermediate Representation                   ║
echo  ║   One-Click Setup and Launch                              ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.

:: ── Step 1: Check Python ─────────────────────────────────────
echo  [1/4] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python not found.
    echo  Please install Python 3.10+ from https://python.org
    echo  Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo         %%i found
echo.

:: ── Step 2: Install dependencies ─────────────────────────────
echo  [2/4] Installing Python dependencies...
echo         flask, flask-cors, requests
echo.
python -m pip install -q flask flask-cors requests
if errorlevel 1 (
    echo  ERROR: pip install failed. Check your internet connection.
    pause
    exit /b 1
)
echo         Dependencies OK
echo.

:: ── Step 3: Check LM Studio ──────────────────────────────────
echo  [3/4] Checking LM Studio...
curl -s -o nul -w "%%{http_code}" http://localhost:1234/v1/models > tmp_lm_check.txt 2>&1
set /p LM_STATUS=<tmp_lm_check.txt
del tmp_lm_check.txt 2>nul

if "%LM_STATUS%"=="200" (
    echo         LM Studio is RUNNING on port 1234
) else (
    echo.
    echo  ⚠  WARNING: LM Studio not detected on port 1234
    echo.
    echo     Please:
    echo       1. Open LM Studio
    echo       2. Load the Qwen 3 model (or any local model)
    echo       3. Start the Local Server (port 1234)
    echo.
    echo     The AIR server will start anyway — you can load
    echo     LM Studio after and refresh the browser.
    echo.
    pause
)
echo.

:: ── Step 4: Launch AIR server ─────────────────────────────────
echo  [4/4] Starting AIR Flask server on http://localhost:5000
echo.
echo  ──────────────────────────────────────────────────────────
echo.
echo   AIR Generator  →  http://localhost:5000
echo   Benchmark      →  http://localhost:5000/benchmark.html
echo.
echo  ──────────────────────────────────────────────────────────
echo.
echo  Opening browser in 3 seconds...
echo  (Press Ctrl+C in this window to stop the server)
echo.

:: Open browser after 3-second delay
start "" cmd /c "timeout /t 3 >nul && start http://localhost:5000"

:: Run server (blocks)
python server.py

pause
