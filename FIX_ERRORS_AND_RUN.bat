@echo off
REM ============================================================
REM Student Dashboard - Fix URL & Static File Errors
REM ============================================================

cd /d "e:\djangoproject\student_dashboard\dashboard"

color 0A
cls
echo.
echo ============================================================
echo   FIXING URL ROUTING AND STATIC FILE ERRORS
echo ============================================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat >nul 2>&1

echo Running error fixes...
echo.

REM Run error fix script
python fix_errors.py

if errorlevel 1 (
    echo.
    echo ERROR: Fix failed!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   STARTING DJANGO SERVER
echo ============================================================
echo.
echo   Your dashboard is ready at:
echo   - http://localhost:8000/
echo   - http://localhost:8000/students/register/
echo   - http://localhost:8000/students/login/
echo   - http://localhost:8000/students/dashboard/
echo   - http://localhost:8000/admin/
echo.
echo   Press CTRL+C to stop
echo.
echo ============================================================
echo.

REM Start server
python manage.py runserver

pause
