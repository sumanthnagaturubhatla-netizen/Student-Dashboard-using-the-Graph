@echo off
REM Student Access Control Setup Script

cd /d "e:\djangoproject\student_dashboard\dashboard"

echo.
echo ================================================================
echo       STUDENT ACCESS CONTROL - SETUP & MIGRATION
echo ================================================================
echo.

echo [1] Running Django migrations...
python manage.py migrate

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [OK] Migration completed successfully!
    echo.
) else (
    echo.
    echo [ERROR] Migration failed!
    echo.
    pause
    exit /b 1
)

echo [2] Checking admin user status...
echo.

REM Create admin user if not exists
echo Would you like to create a superuser/admin account? (y/n)
set /p create_admin="Enter choice (y/n): "

if /i "%create_admin%"=="y" (
    echo.
    echo Creating superuser account...
    python manage.py createsuperuser
    echo.
)

echo.
echo ================================================================
echo       SETUP COMPLETE!
echo ================================================================
echo.
echo Next steps:
echo   1. Start the server: python manage.py runserver
echo   2. Go to http://localhost:8000/students/admin-login/
echo   3. Login with your admin credentials
echo   4. Manage student access from the dashboard
echo.
pause
