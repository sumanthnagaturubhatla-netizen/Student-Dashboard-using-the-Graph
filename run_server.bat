@echo off
REM Student Dashboard - Automated Setup Script
REM This script sets up the Django project and runs the server

cd /d "e:\djangoproject\student_dashboard\dashboard"

echo.
echo ============================================================
echo Student Dashboard - Automated Setup
echo ============================================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo [1/6] Creating virtual environment...
    python -m venv venv
    echo Virtual environment created!
) else (
    echo [1/6] Virtual environment already exists
)

REM Activate virtual environment
echo [2/6] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo [3/6] Installing dependencies...
pip install -q Django==4.2.0 django-extensions==3.2.3

REM Create Django project
if not exist "dashboard" (
    echo [4/6] Creating Django project...
    django-admin startproject dashboard .
) else (
    echo [4/6] Django project already exists
)

REM Create app
if not exist "students" (
    echo [5/6] Creating students app...
    python manage.py startapp students
) else (
    echo [5/6] Students app already exists
)

REM Create templates directory
if not exist "templates" mkdir templates
if not exist "static" mkdir static
if not exist "static\css" mkdir static\css
if not exist "static\js" mkdir static\js

echo [6/6] Running migrations...
python manage.py makemigrations students 2>nul
python manage.py migrate

echo.
echo ============================================================
echo Setup Complete! Running Django Server...
echo ============================================================
echo.
echo Access your dashboard at: http://localhost:8000
echo Press CTRL+C to stop the server
echo.

python manage.py runserver
