@echo off
echo Starting AI Chat Assistant...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if setup was run
if not exist "venv" (
    echo First time setup required...
    echo Running setup.py to install dependencies...
    python setup.py
    if errorlevel 1 (
        echo Setup failed! Please check the error messages above.
        pause
        exit /b 1
    )
)

REM Run the application
echo Launching AI Chat Assistant...
venv\Scripts\python.exe -m gui.app

pause
