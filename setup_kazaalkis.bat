@echo off
REM KazaALKIS Setup Script for Windows
REM This script initializes the KazaALKIS environment

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║      KazaALKIS - Daily Greek Calendar Setup Script        ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ ERROR: Python is not installed or not in PATH
    echo   Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo ✓ Python found
python --version

REM Get project directory and AI workspace
set PROJECT_DIR=%~dp0
if "%AI_ROOT%"=="" set AI_ROOT=E:\AI
set VENV_DIR=%AI_ROOT%\venvs\KazaALKIS
echo.
echo Project Directory: %PROJECT_DIR%

REM Create virtual environment
echo.
echo Creating virtual environment...
python -m venv "%VENV_DIR%"

if %errorlevel% neq 0 (
    echo ✗ ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo ✓ Virtual environment created

REM Activate virtual environment
echo.
echo Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements from AI directory
echo.
echo Installing dependencies...
if exist "%PROJECT_DIR%requirements.txt" pip install -r "%PROJECT_DIR%requirements.txt"

if %errorlevel% neq 0 (
    echo ✗ ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo ✓ Dependencies installed

REM Create necessary directories
echo.
echo Creating project directories...
if not exist "%AI_ROOT%\logs\KazaALKIS" mkdir "%AI_ROOT%\logs\KazaALKIS"
if not exist "%AI_ROOT%\outputs\KazaALKIS" mkdir "%AI_ROOT%\outputs\KazaALKIS"

echo ✓ Directories created

REM Initialize database
echo.
echo Initializing database...
cd /d "%PROJECT_DIR%"
python -c "from src.database import KazaALKISDatabase; db = KazaALKISDatabase(); db.connect(); db.initialize_schema(); db.import_namedays_from_json('data/kazamias_namedays_2026.json'); db.import_quotes_from_json('data/kazamias_quotes_2026.json'); db.import_holidays_from_json('data/greek_holidays_2026.json'); db.import_fasting_from_json('data/fasting_periods_2026.json'); db.close(); print('✓ Database initialized')"

if %errorlevel% neq 0 (
    echo ✗ WARNING: Database initialization had issues
    echo   You can initialize manually using the Python launcher
)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║              Setup Completed Successfully!                ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Next steps:
echo  1. Edit contacts in: data\contacts.json
echo  2. Run Python launcher: python KazaALKIS_launcher.py
echo.
pause
