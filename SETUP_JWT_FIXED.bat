@echo off
REM Simple JWT Setup & Test - Fixed Version
REM This script applies migrations and runs the test suite

setlocal enabledelayedexpansion

echo.
echo ================================================================
echo JWT AUTHENTICATION - QUICK SETUP (FIXED)
echo ================================================================
echo.

cd /d "e:\djangoproject\student_dashboard\dashboard"

echo [1/3] Running Django system check...
python manage.py check
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Django system check failed!
    pause
    exit /b 1
)
echo OK - System check passed
echo.

echo [2/3] Running database migrations...
python manage.py migrate
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Migrations failed!
    pause
    exit /b 1
)
echo OK - Database updated
echo.

echo [3/3] Running comprehensive tests...
python setup_jwt_complete.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Tests failed!
    echo.
    echo Try running these manually:
    echo   python verify_jwt_setup.py
    echo   python manage.py check
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================
echo SUCCESS - JWT Authentication is fully set up!
echo ================================================================
echo.
echo NEXT STEPS:
echo   1. Start server: python manage.py runserver
echo   2. Open browser: http://localhost:8000/students/login/
echo   3. Test login with: jwttest / jwttest123 (created by tests)
echo.
pause
