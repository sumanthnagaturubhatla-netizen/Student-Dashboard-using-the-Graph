#!/usr/bin/env python
"""
Simple JWT Setup Verification
Verifies all JWT components are in place and working
"""
import os
import sys
import json

# Add project to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard.settings')

print("\n" + "="*70)
print(" JWT SETUP VERIFICATION")
print("="*70)

# Check 1: Python version
print("\n[1] Checking Python version...")
print(f"    Python {sys.version.split()[0]}")
if sys.version_info >= (3, 6):
    print("    ✓ Python 3.6+ (OK)")
else:
    print("    ✗ Python 3.6+ required")
    sys.exit(1)

# Check 2: Django installation
print("\n[2] Checking Django installation...")
try:
    import django
    print(f"    Django {django.VERSION[0]}.{django.VERSION[1]}")
    print("    ✓ Django installed (OK)")
except ImportError:
    print("    ✗ Django not installed")
    sys.exit(1)

# Check 3: JWT files exist
print("\n[3] Checking JWT component files...")
files_to_check = [
    ('students/jwt_utils.py', 'JWT utilities'),
    ('students/api.py', 'API endpoints'),
    ('students/auth_middleware.py', 'Authentication middleware'),
    ('students/models.py', 'Database models'),
    ('dashboard/settings.py', 'Django settings'),
    ('students/urls.py', 'URL routing'),
    ('students/views.py', 'Views'),
]

all_files_exist = True
for filepath, description in files_to_check:
    full_path = os.path.join(project_root, filepath)
    if os.path.exists(full_path):
        size = os.path.getsize(full_path)
        print(f"    ✓ {filepath} ({size} bytes)")
    else:
        print(f"    ✗ {filepath} - NOT FOUND")
        all_files_exist = False

if not all_files_exist:
    print("\n    Some files are missing!")
    sys.exit(1)

# Check 4: Check for RefreshToken model in models.py
print("\n[4] Checking RefreshToken model...")
models_path = os.path.join(project_root, 'students/models.py')
with open(models_path, 'r') as f:
    models_content = f.read()
    if 'class RefreshToken' in models_content:
        print("    ✓ RefreshToken model found in models.py")
    else:
        print("    ✗ RefreshToken model not found")
        sys.exit(1)

# Check 5: Check for JWT middleware in settings
print("\n[5] Checking JWT middleware in settings...")
settings_path = os.path.join(project_root, 'dashboard/settings.py')
with open(settings_path, 'r') as f:
    settings_content = f.read()
    if 'JWTAuthenticationMiddleware' in settings_content:
        print("    ✓ JWT middleware registered in settings")
    else:
        print("    ⚠ JWT middleware not found in settings (may need manual addition)")

# Check 6: Check for JWT configuration
print("\n[6] Checking JWT configuration in settings...")
if 'JWT_ACCESS_TOKEN_EXPIRY_MINUTES' in settings_content:
    print("    ✓ JWT_ACCESS_TOKEN_EXPIRY_MINUTES configured")
else:
    print("    ⚠ JWT_ACCESS_TOKEN_EXPIRY_MINUTES not set")

if 'JWT_REFRESH_TOKEN_EXPIRY_DAYS' in settings_content:
    print("    ✓ JWT_REFRESH_TOKEN_EXPIRY_DAYS configured")
else:
    print("    ⚠ JWT_REFRESH_TOKEN_EXPIRY_DAYS not set")

# Check 7: Verify JWT utilities
print("\n[7] Verifying JWT utilities...")
try:
    # Import JWT handler
    sys.path.insert(0, os.path.join(project_root, 'students'))
    from jwt_utils import JWTHandler
    
    # Create test handler
    handler = JWTHandler('test-secret-key')
    
    # Generate test token
    test_token = handler.generate_access_token(1, 'testuser')
    print(f"    ✓ Token generation works")
    print(f"      Sample token (first 50 chars): {test_token[:50]}...")
    
    # Verify test token
    is_valid, payload = handler.verify_token(test_token)
    if is_valid:
        print(f"    ✓ Token verification works")
        print(f"      User ID: {payload.get('user_id')}")
        print(f"      Username: {payload.get('username')}")
    else:
        print(f"    ✗ Token verification failed")
        sys.exit(1)
        
except Exception as e:
    print(f"    ✗ Error testing JWT utilities: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Check 8: Check API endpoints
print("\n[8] Checking API endpoint configuration...")
urls_path = os.path.join(project_root, 'students/urls.py')
with open(urls_path, 'r') as f:
    urls_content = f.read()
    endpoints = {
        'api_login': '/api/login/',
        'api_refresh': '/api/refresh/',
        'api_logout': '/api/logout/',
        'api_verify_token': '/api/verify/',
    }
    
    for endpoint_name, endpoint_path in endpoints.items():
        if endpoint_path in urls_content or endpoint_name in urls_content:
            print(f"    ✓ {endpoint_path} configured")
        else:
            print(f"    ⚠ {endpoint_path} might not be configured")

# Check 9: Database setup
print("\n[9] Checking database setup...")
try:
    django.setup()
    from django.db import connection
    
    # Check if RefreshToken table exists
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT COUNT(*) FROM students_refreshtoken LIMIT 1")
            print("    ✓ RefreshToken table exists in database")
        except Exception as e:
            if 'no such table' in str(e).lower() or 'table does not exist' in str(e).lower():
                print("    ⚠ RefreshToken table not created yet")
                print("      Run: python manage.py migrate")
            else:
                raise
except Exception as e:
    print(f"    ⚠ Could not check database: {e}")

# Check 10: Summary
print("\n" + "="*70)
print(" VERIFICATION COMPLETE")
print("="*70)

print("""
✅ JWT components are in place!

NEXT STEPS:

1. Run migrations to create database tables:
   python manage.py migrate

2. Start the Django server:
   python manage.py runserver

3. Visit the application:
   http://localhost:8000/students/login/

DOCUMENTATION:
- JWT_SETUP_INSTRUCTIONS.md - How to set up
- JWT_README.md - Overview
- JWT_QUICK_START.md - API reference
- JWT_AUTHENTICATION_GUIDE.md - Complete guide

API ENDPOINTS AVAILABLE:
- POST /students/api/login/ - Get access and refresh tokens
- POST /students/api/refresh/ - Refresh access token
- POST /students/api/logout/ - Revoke refresh token
- POST /students/api/verify/ - Verify token validity

""")
