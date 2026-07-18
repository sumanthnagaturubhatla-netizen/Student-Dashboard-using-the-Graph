@echo off
REM ============================================================
REM Student Dashboard - Emergency Fix & Run
REM Fixes missing dashboard package and runs server
REM ============================================================

cd /d "e:\djangoproject\student_dashboard\dashboard"

color 0A
cls
echo.
echo ============================================================
echo   STUDENT DASHBOARD - EMERGENCY FIX & RUN
echo ============================================================
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat >nul 2>&1

echo Running emergency fix script...
echo.

REM Run emergency fix
python emergency_fix.py

if errorlevel 1 (
    echo.
    echo ERROR: Fix script failed!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   STARTING DJANGO SERVER
echo ============================================================
echo.
echo   Access your dashboard at:
echo   - http://localhost:8000
echo   - http://localhost:8000/students/register/
echo   - http://localhost:8000/students/dashboard/
echo   - http://localhost:8000/admin/
echo.
echo   Press CTRL+C to stop the server
echo.
echo ============================================================
echo.

REM Start server
python manage.py runserver

pause
