@echo off
REM Complete JWT Authentication Setup & Testing
REM This script runs the entire JWT implementation process

echo.
echo ================================================================
echo JWT AUTHENTICATION - COMPLETE SETUP & TESTING
echo ================================================================
echo.

cd /d "e:\djangoproject\student_dashboard\dashboard"

REM Run the comprehensive setup script
echo Running complete setup and testing...
echo.

python setup_jwt_complete.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================================================
    echo SUCCESS - JWT Authentication is fully set up and tested!
    echo ================================================================
    echo.
    echo Next: Start the server with: python manage.py runserver
    echo.
    pause
) else (
    echo.
    echo ERROR - Setup failed!
    echo.
    pause
    exit /b 1
)
