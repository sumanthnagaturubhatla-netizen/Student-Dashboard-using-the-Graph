#!/usr/bin/env python3
"""
Student Dashboard - Automatic Setup Script
This script sets up the entire Django project with all files
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.absolute()
os.chdir(PROJECT_ROOT)

print("\n" + "="*70)
print("🎓 STUDENT DASHBOARD - AUTOMATIC SETUP")
print("="*70 + "\n")

# Step 1: Create virtual environment
print("📦 [1/8] Setting up virtual environment...")
venv_path = PROJECT_ROOT / "venv"
if not venv_path.exists():
    subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    print("✅ Virtual environment created")
else:
    print("✅ Virtual environment already exists")

# Step 2: Install requirements
print("\n📦 [2/8] Installing dependencies...")
subprocess.run([
    sys.executable, "-m", "pip", "install", "-q",
    "Django==4.2.0", "django-extensions==3.2.3"
], check=True)
print("✅ Dependencies installed")

# Step 3: Create Django project
print("\n📦 [3/8] Creating Django project...")
if not (PROJECT_ROOT / "manage.py").exists():
    subprocess.run([
        sys.executable, "-m", "django",
        "startproject", "dashboard", "."
    ], check=True)
    print("✅ Django project created")
else:
    print("✅ Django project already exists")

# Step 4: Create app
print("\n📦 [4/8] Creating students app...")
if not (PROJECT_ROOT / "students").exists():
    subprocess.run([
        sys.executable, "manage.py",
        "startapp", "students"
    ], check=True)
    print("✅ Students app created")
else:
    print("✅ Students app already exists")

# Step 5: Create directories
print("\n📦 [5/8] Creating directories...")
dirs = ["templates", "static", "static/css", "static/js", "static/img"]
for d in dirs:
    (PROJECT_ROOT / d).mkdir(exist_ok=True)
print("✅ Directories created")

# Step 6: Copy configuration files
print("\n📦 [6/8] Copying configuration files...")
files_to_copy = {
    "dashboard_settings.py": "dashboard/settings.py",
    "dashboard_urls_config.py": "dashboard/urls.py",
    "dashboard_wsgi.py": "dashboard/wsgi.py",
    "students_models.py": "students/models.py",
    "students_forms.py": "students/forms.py",
    "students_views.py": "students/views.py",
    "students_urls.py": "students/urls.py",
    "students_admin.py": "students/admin.py",
    "templates_base.html": "templates/base.html",
    "templates_register.html": "templates/register.html",
    "templates_login.html": "templates/login.html",
    "templates_dashboard.html": "templates/dashboard.html",
    "templates_profile.html": "templates/profile.html",
}

for source, dest in files_to_copy.items():
    src_path = PROJECT_ROOT / source
    dest_path = PROJECT_ROOT / dest
    if src_path.exists():
        shutil.copy2(src_path, dest_path)
        print(f"  ✓ Copied {source}")

print("✅ Configuration files copied")

# Step 7: Run migrations
print("\n📦 [7/8] Running database migrations...")
subprocess.run([
    sys.executable, "manage.py",
    "makemigrations", "students"
], capture_output=True)
subprocess.run([
    sys.executable, "manage.py",
    "migrate"
], capture_output=True)
print("✅ Migrations completed")

# Step 8: Summary and run server
print("\n" + "="*70)
print("✨ SETUP COMPLETE!")
print("="*70 + "\n")

print("📊 Project Summary:")
print(f"  • Project Root: {PROJECT_ROOT}")
print(f"  • Django Version: 4.2.0")
print(f"  • Database: SQLite (db.sqlite3)")
print(f"  • Templates: {len(list(PROJECT_ROOT.glob('templates/*.html')))} created")
print(f"  • Apps: students, admin, auth, etc.")

print("\n🌐 Starting Django Development Server...")
print("   Access Dashboard: http://localhost:8000")
print("   Admin Panel: http://localhost:8000/admin")
print("   Registration: http://localhost:8000/students/register/")
print("\n💡 Press CTRL+C to stop the server\n")

# Run server
subprocess.run([sys.executable, "manage.py", "runserver"])
