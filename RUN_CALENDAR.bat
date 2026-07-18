@echo off
REM ============================================================
REM Student Dashboard with Calendar Feature
REM ============================================================
echo.
echo Starting Django Server with Calendar Feature...
echo.

cd /d "e:\djangoproject\student_dashboard\dashboard"

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run server
python manage.py runserver

pause
