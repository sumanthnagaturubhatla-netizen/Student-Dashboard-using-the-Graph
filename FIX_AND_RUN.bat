@echo off
REM ============================================================
REM Student Dashboard - Complete Fix & Run Script
REM ============================================================

cd /d "e:\djangoproject\student_dashboard\dashboard"

color 0A
cls
echo.
echo ============================================================
echo   STUDENT DASHBOARD - FIXING SETUP AND RUNNING SERVER
echo ============================================================
echo.

REM Step 1: Activate virtual environment
echo [1/2] Activating virtual environment...
call venv\Scripts\activate.bat >nul 2>&1
if errorlevel 1 (
    echo   Error: Virtual environment not found!
    echo   Creating it now...
    python -m venv venv
    call venv\Scripts\activate.bat
)
echo   Activated: venv

REM Step 2: Run fix script
echo [2/2] Running setup fix...
python fix_setup.py

REM Final message
echo.
echo ============================================================
echo   SETUP COMPLETE! STARTING SERVER...
echo ============================================================
echo.
echo   Dashboard: http://localhost:8000
echo   Admin:     http://localhost:8000/admin/
echo   Register:  http://localhost:8000/students/register/
echo.
echo   Press CTRL+C to stop
echo.
echo ============================================================
echo.

REM Start server
python manage.py runserver

pause
