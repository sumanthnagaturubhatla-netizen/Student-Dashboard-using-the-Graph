@echo off
REM Start Django server with calendar and navigation features
cd /d e:\djangoproject\student_dashboard\dashboard

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run Django server
python manage.py runserver

pause
