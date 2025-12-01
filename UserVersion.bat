@echo off
echo ========================================
echo        MarketAI User Edition
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found. Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Run user version
python "%~dp0user_version.py"

pause
