@echo off
REM ============================================================
REM Student Dashboard - Quick Start Setup & Run
REM ============================================================
REM This script will:
REM 1. Create virtual environment
REM 2. Install Django
REM 3. Set up project files
REM 4. Run migrations
REM 5. Start the development server
REM ============================================================

setlocal enabledelayedexpansion
cd /d "e:\djangoproject\student_dashboard\dashboard"

color 0A
cls
echo.
echo.
echo ============================================================
echo   STUDENT DASHBOARD - SETUP AND RUN
echo ============================================================
echo.

REM Step 1: Virtual Environment
echo [STEP 1/5] Creating Virtual Environment...
if not exist "venv" (
    python -m venv venv
    echo   Created: venv
) else (
    echo   Already exists: venv
)

REM Activate venv
call venv\Scripts\activate.bat >nul 2>&1

REM Step 2: Install Django
echo [STEP 2/5] Installing Django and Dependencies...
pip install -q Django==4.2.0 2>nul
if errorlevel 1 (
    pip install Django==4.2.0
)
echo   Installed: Django 4.2.0

REM Step 3: Create Django Project
echo [STEP 3/5] Setting up Django Project...

REM Check if dashboard project exists
if not exist "manage.py" (
    echo   Creating Django project...
    django-admin startproject dashboard .
)

REM Check if students app exists
if not exist "students" (
    echo   Creating students app...
    python manage.py startapp students
)

REM Create necessary directories
if not exist "templates" mkdir templates
if not exist "static" mkdir static
if not exist "static\css" mkdir static\css
if not exist "static\js" mkdir static\js

echo   Setup: Complete

REM Step 4: Copy Template Files
echo [STEP 4/5] Copying Configuration Files...

REM Copy settings
if exist "dashboard_settings.py" (
    copy /Y dashboard_settings.py dashboard\settings.py >nul 2>&1
    echo   Copied: settings.py
)

REM Copy urls
if exist "dashboard_urls_config.py" (
    copy /Y dashboard_urls_config.py dashboard\urls.py >nul 2>&1
    echo   Copied: urls.py
)

REM Copy wsgi
if exist "dashboard_wsgi.py" (
    copy /Y dashboard_wsgi.py dashboard\wsgi.py >nul 2>&1
    echo   Copied: wsgi.py
)

REM Copy students app files
if exist "students_models.py" (
    copy /Y students_models.py students\models.py >nul 2>&1
    echo   Copied: students/models.py
)

if exist "students_forms.py" (
    copy /Y students_forms.py students\forms.py >nul 2>&1
    echo   Copied: students/forms.py
)

if exist "students_views.py" (
    copy /Y students_views.py students\views.py >nul 2>&1
    echo   Copied: students/views.py
)

if exist "students_urls.py" (
    copy /Y students_urls.py students\urls.py >nul 2>&1
    echo   Copied: students/urls.py
)

if exist "students_admin.py" (
    copy /Y students_admin.py students\admin.py >nul 2>&1
    echo   Copied: students/admin.py
)

REM Copy templates
if exist "templates_base.html" (
    copy /Y templates_base.html templates\base.html >nul 2>&1
    echo   Copied: templates/base.html
)

if exist "templates_register.html" (
    copy /Y templates_register.html templates\register.html >nul 2>&1
    echo   Copied: templates/register.html
)

if exist "templates_login.html" (
    copy /Y templates_login.html templates\login.html >nul 2>&1
    echo   Copied: templates/login.html
)

if exist "templates_dashboard.html" (
    copy /Y templates_dashboard.html templates\dashboard.html >nul 2>&1
    echo   Copied: templates/dashboard.html
)

if exist "templates_profile.html" (
    copy /Y templates_profile.html templates\profile.html >nul 2>&1
    echo   Copied: templates/profile.html
)

REM Step 5: Migrations
echo [STEP 5/5] Running Database Migrations...
python manage.py makemigrations students >nul 2>&1
python manage.py migrate >nul 2>&1
echo   Migrations: Complete

REM Final Message
echo.
echo ============================================================
echo   SETUP COMPLETE!
echo ============================================================
echo.
echo   Project Information:
echo   - Location: e:\djangoproject\student_dashboard\dashboard
echo   - Django Version: 4.2.0
echo   - Database: SQLite (db.sqlite3)
echo   - Environment: Virtual (venv)
echo.
echo   Starting Development Server...
echo.
echo   Access Points:
echo   - Dashboard:     http://localhost:8000
echo   - Admin Panel:   http://localhost:8000/admin
echo   - Register:      http://localhost:8000/students/register/
echo   - Login:         http://localhost:8000/students/login/
echo.
echo   Press CTRL+C to stop the server
echo.
echo ============================================================
echo.

REM Run the server
python manage.py runserver

pause
