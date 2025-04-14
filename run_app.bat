@echo off
TITLE Student Management System
echo Starting Student Management System...

REM Check if virtual environment exists, create if it doesn't
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment.
        echo Please make sure Python is installed and in your PATH.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

REM Install dependencies if needed
echo Checking dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Warning: Failed to install some dependencies.
)

REM Create data directory if it doesn't exist
if not exist data mkdir data

REM Create logs directory if it doesn't exist
if not exist logs mkdir logs

REM Run the application
echo Starting application...
python main.py
if %errorlevel% neq 0 (
    echo Application terminated with errors.
    pause
)

REM Deactivate virtual environment
call venv\Scripts\deactivate

exit /b 0
