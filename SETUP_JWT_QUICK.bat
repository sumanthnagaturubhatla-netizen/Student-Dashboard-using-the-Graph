@echo off
REM Quick JWT Setup - Direct Python Execution
REM This is the simplest way to set up JWT authentication

setlocal enabledelayedexpansion

echo.
echo ================================================================
echo JWT AUTHENTICATION - QUICK SETUP
echo ================================================================
echo.

cd /d "e:\djangoproject\student_dashboard\dashboard"

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo [1/5] Running Django system check...
python manage.py check
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Django system check failed!
    pause
    exit /b 1
)
echo OK - No issues found

echo.
echo [2/5] Running database migrations...
python manage.py migrate
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Migrations failed!
    pause
    exit /b 1
)
echo OK - Database updated

echo.
echo [3/5] Collecting static files...
python manage.py collectstatic --noinput
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Static files collection failed!
    pause
    exit /b 1
)
echo OK - Static files ready

echo.
echo [4/5] Running JWT tests...
python setup_jwt_complete.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Setup tests failed!
    pause
    exit /b 1
)

echo.
echo ================================================================
echo SUCCESS!
echo ================================================================
echo.
echo Your JWT authentication is fully set up!
echo.
echo NEXT STEP: Start the server
echo   Command: python manage.py runserver
echo.
echo Then visit: http://localhost:8000/students/login/
echo.
echo Test Credentials:
echo   Username: jwttest
echo   Password: jwttest123
echo.
pause
