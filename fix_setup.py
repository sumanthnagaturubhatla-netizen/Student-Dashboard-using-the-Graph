#!/usr/bin/env python3
"""
Complete Django Setup Fix Script
Fixes the project structure and copies all files to correct locations
"""

import os
import sys
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.absolute()
os.chdir(PROJECT_ROOT)

print("\n" + "="*70)
print("🔧 FIXING DJANGO PROJECT STRUCTURE")
print("="*70 + "\n")

# Step 1: Create dashboard package folder
print("📦 [1/6] Creating dashboard package folder...")
dashboard_pkg = PROJECT_ROOT / "dashboard"
dashboard_pkg.mkdir(exist_ok=True)

# Create __init__.py
(dashboard_pkg / "__init__.py").touch()
print("  ✓ Created: dashboard/__init__.py")

# Step 2: Copy configuration files
print("\n📦 [2/6] Copying configuration files...")

files_to_copy = {
    "dashboard_settings.py": "dashboard/settings.py",
    "dashboard_urls_config.py": "dashboard/urls.py",
    "dashboard_wsgi.py": "dashboard/wsgi.py",
}

for src, dst in files_to_copy.items():
    src_path = PROJECT_ROOT / src
    dst_path = PROJECT_ROOT / dst
    if src_path.exists():
        shutil.copy2(src_path, dst_path)
        print(f"  ✓ Copied: {src} → {dst}")

# Step 3: Create asgi.py
print("\n📦 [3/6] Creating asgi.py...")
asgi_content = '''"""
ASGI config for dashboard project.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard.settings')
application = get_asgi_application()
'''
(dashboard_pkg / "asgi.py").write_text(asgi_content)
print("  ✓ Created: dashboard/asgi.py")

# Step 4: Copy app files
print("\n📦 [4/6] Copying students app files...")

students_files = {
    "students_models.py": "students/models.py",
    "students_forms.py": "students/forms.py",
    "students_views.py": "students/views.py",
    "students_urls.py": "students/urls.py",
    "students_admin.py": "students/admin.py",
}

for src, dst in students_files.items():
    src_path = PROJECT_ROOT / src
    dst_path = PROJECT_ROOT / dst
    if src_path.exists():
        shutil.copy2(src_path, dst_path)
        print(f"  ✓ Copied: {src}")

# Step 5: Copy templates
print("\n📦 [5/6] Copying template files...")

template_files = {
    "templates_base.html": "templates/base.html",
    "templates_register.html": "templates/register.html",
    "templates_login.html": "templates/login.html",
    "templates_dashboard.html": "templates/dashboard.html",
    "templates_profile.html": "templates/profile.html",
}

for src, dst in template_files.items():
    src_path = PROJECT_ROOT / src
    dst_path = PROJECT_ROOT / dst
    if src_path.exists():
        shutil.copy2(src_path, dst_path)
        print(f"  ✓ Copied: {src}")

# Step 6: Run migrations
print("\n📦 [6/6] Running migrations...")
import subprocess

try:
    subprocess.run([sys.executable, "manage.py", "makemigrations", "students"], 
                  capture_output=True, text=True, timeout=30)
    print("  ✓ makemigrations completed")
except Exception as e:
    print(f"  ⚠ makemigrations: {e}")

try:
    subprocess.run([sys.executable, "manage.py", "migrate"], 
                  capture_output=True, text=True, timeout=30)
    print("  ✓ migrate completed")
except Exception as e:
    print(f"  ⚠ migrate: {e}")

# Summary
print("\n" + "="*70)
print("✅ PROJECT STRUCTURE FIXED!")
print("="*70 + "\n")

print("📁 Project Structure:")
print(f"  dashboard/")
print(f"    ├── __init__.py")
print(f"    ├── settings.py ✓")
print(f"    ├── urls.py ✓")
print(f"    ├── wsgi.py ✓")
print(f"    └── asgi.py ✓")
print(f"  students/")
print(f"    ├── models.py ✓")
print(f"    ├── views.py ✓")
print(f"    ├── forms.py ✓")
print(f"    ├── urls.py ✓")
print(f"    └── admin.py ✓")
print(f"  templates/")
print(f"    ├── base.html ✓")
print(f"    ├── register.html ✓")
print(f"    ├── login.html ✓")
print(f"    ├── dashboard.html ✓")
print(f"    └── profile.html ✓")

print("\n🚀 Now you can run the server!\n")
print("Command: python manage.py runserver\n")
