import os
import sys
import shutil
from pathlib import Path

# Change to project directory
project_root = Path(__file__).parent
os.chdir(project_root)

print("\n" + "="*70)
print("🚨 EMERGENCY FIX - Creating Django Structure")
print("="*70 + "\n")

try:
    # 1. Create dashboard package
    print("Creating dashboard package...")
    dashboard_dir = project_root / "dashboard"
    dashboard_dir.mkdir(exist_ok=True)
    
    # Create __init__.py
    init_file = dashboard_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text('')
    print("  ✓ Created dashboard/__init__.py")
    
    # 2. Copy settings.py
    print("\nCopying settings...")
    settings_src = project_root / "dashboard_settings.py"
    settings_dst = dashboard_dir / "settings.py"
    if settings_src.exists():
        shutil.copy2(settings_src, settings_dst)
        print("   Copied settings.py")
    
    # 3. Copy urls.py
    urls_src = project_root / "dashboard_urls_config.py"
    urls_dst = dashboard_dir / "urls.py"
    if urls_src.exists():
        shutil.copy2(urls_src, urls_dst)
        print("  Copied urls.py")
    
    # 4. Copy wsgi.py
    wsgi_src = project_root / "dashboard_wsgi.py"
    wsgi_dst = dashboard_dir / "wsgi.py"
    if wsgi_src.exists():
        shutil.copy2(wsgi_src, wsgi_dst)
        print("   Copied wsgi.py")
    
    # 5. Create asgi.py
    asgi_content = '''"""ASGI config for dashboard project."""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard.settings')
application = get_asgi_application()
'''
    asgi_dst = dashboard_dir / "asgi.py"
    asgi_dst.write_text(asgi_content)
    print("   Created asgi.py")
    
    # 6. Copy students app files
    print("\nCopying students app files...")
    students_files = [
        ("students_models.py", "models.py"),
        ("students_forms.py", "forms.py"),
        ("students_views.py", "views.py"),
        ("students_admin.py", "admin.py"),
    ]
    
    for src_name, dst_name in students_files:
        src = project_root / src_name
        dst = project_root / "students" / dst_name
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  Copied {dst_name}")
    
    # Create students urls.py
    students_urls_src = project_root / "students_urls.py"
    students_urls_dst = project_root / "students" / "urls.py"
    if students_urls_src.exists():
        shutil.copy2(students_urls_src, students_urls_dst)
        print("   Copied students/urls.py")
    
    # 7. Copy template files
    print("\nCopying templates...")
    template_files = [
        ("templates_base.html", "base.html"),
        ("templates_register.html", "register.html"),
        ("templates_login.html", "login.html"),
        ("templates_dashboard.html", "dashboard.html"),
        ("templates_profile.html", "profile.html"),
    ]
    
    for src_name, dst_name in template_files:
        src = project_root / src_name
        dst = project_root / "templates" / dst_name
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  ✓ Copied {dst_name}")
    
    print("\n" + "="*70)
    print("ALL FILES CREATED SUCCESSFULLY!")
    print("="*70 + "\n")
    
    # Now run migrations
    print("Running migrations...\n")
    import subprocess
    
    result = subprocess.run(
        [sys.executable, "manage.py", "makemigrations", "students"],
        capture_output=False,
        text=True
    )
    
    if result.returncode == 0:
        print("\n✓ Migrations created\n")
    
    result = subprocess.run(
        [sys.executable, "manage.py", "migrate"],
        capture_output=False,
        text=True
    )
    
    if result.returncode == 0:
        print("\n✓ Database migrated\n")
    
    print("="*70)
    print("🎉 READY TO RUN!")
    print("="*70)
    print("\nNext command: python manage.py runserver\n")
    
except Exception as e:
    print(f"\n❌ Error: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)
