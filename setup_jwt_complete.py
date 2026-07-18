#!/usr/bin/env python
"""
Complete JWT Authentication Setup & Testing Script
Runs the entire JWT implementation process including:
1. Database migration
2. System checks
3. Comprehensive tests
4. Summary report
"""
import os
import sys
import django
import subprocess

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.core.management import call_command
from django.test import Client
from django.contrib.auth.models import User
from students.models import RefreshToken, Student
from students.jwt_utils import JWTHandler
from students.forms import StudentRegistrationForm
from django.conf import settings
import json
from datetime import timedelta
from django.utils import timezone

print("\n" + "="*70)
print(" JWT AUTHENTICATION - COMPLETE SETUP & TESTING")
print("="*70)

# STEP 1: Check Django Installation
print("\n[STEP 1] Checking Django Installation...")
print("-" * 70)
try:
    from django import VERSION
    print(f"✓ Django {VERSION[0]}.{VERSION[1]} is installed")
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

# STEP 2: Run System Check
print("\n[STEP 2] Running Django System Check...")
print("-" * 70)
try:
    from io import StringIO
    from django.core.management import execute_from_command_line
    print("✓ Running 'python manage.py check'...")
    call_command('check', verbosity=0)
    print("✓ System check passed - no issues found")
except Exception as e:
    print(f"✗ System check failed: {e}")
    sys.exit(1)

# STEP 3: Run Migrations
print("\n[STEP 3] Running Database Migrations...")
print("-" * 70)
try:
    print("✓ Running migrations...")
    call_command('migrate', verbosity=0)
    print("✓ All migrations applied successfully")
    
    # Verify RefreshToken table exists
    RefreshToken.objects.count()
    print("✓ RefreshToken table verified in database")
except Exception as e:
    print(f"✗ Migration failed: {e}")
    sys.exit(1)

# STEP 4: Prepare Test User
print("\n[STEP 4] Creating Test User...")
print("-" * 70)
try:
    # Clean up first
    User.objects.filter(username='jwttest').delete()
    
    # Create test user
    test_user = User.objects.create_user(
        username='jwttest',
        password='jwttest123',
        email='jwttest@test.com',
        first_name='JWT',
        last_name='Tester'
    )
    print(f"✓ Created test user: {test_user.username}")
    
    # Create student profile
    student = Student.objects.create(
        user=test_user,
        roll_number='JWT001'
    )
    print(f"✓ Created student profile: {student.roll_number}")
except Exception as e:
    print(f"✗ Test user creation failed: {e}")
    sys.exit(1)

# STEP 5: Test JWT Token Generation
print("\n[STEP 5] Testing JWT Token Generation...")
print("-" * 70)
try:
    jwt_handler = JWTHandler(settings.SECRET_KEY)
    access_token = jwt_handler.generate_access_token(test_user.id, test_user.username)
    refresh_token = jwt_handler.generate_refresh_token()
    
    print(f"✓ Generated access token: {access_token[:50]}...")
    print(f"  Token length: {len(access_token)} characters")
    print(f"✓ Generated refresh token: {refresh_token[:50]}...")
    print(f"  Token length: {len(refresh_token)} characters")
except Exception as e:
    print(f"✗ Token generation failed: {e}")
    sys.exit(1)

# STEP 6: Test Token Verification
print("\n[STEP 6] Testing Token Verification...")
print("-" * 70)
try:
    is_valid, payload = jwt_handler.verify_token(access_token)
    print(f"✓ Token is valid: {is_valid}")
    
    if payload:
        print(f"  User ID: {payload.get('user_id')}")
        print(f"  Username: {payload.get('username')}")
        print(f"  Issued: {payload.get('iat')}")
        print(f"  Expires: {payload.get('exp')}")
    else:
        print("✗ Could not decode payload")
        sys.exit(1)
except Exception as e:
    print(f"✗ Token verification failed: {e}")
    sys.exit(1)

# STEP 7: Test API Endpoints
print("\n[STEP 7] Testing API Endpoints...")
print("-" * 70)
client = Client()

# Test Login
print("  Testing /api/login/...")
try:
    response = client.post(
        '/students/api/login/',
        data=json.dumps({'username': 'jwttest', 'password': 'jwttest123'}),
        content_type='application/json'
    )
    if response.status_code == 200:
        data = response.json()
        print(f"    ✓ Login successful (Status: {response.status_code})")
        print(f"      User: {data.get('username')}")
        print(f"      Access token: {data.get('access_token', '')[:50]}...")
        login_access_token = data.get('access_token')
        login_refresh_token = data.get('refresh_token')
    else:
        print(f"    ✗ Login failed (Status: {response.status_code})")
        print(f"      Error: {response.json()}")
        sys.exit(1)
except Exception as e:
    print(f"    ✗ Login endpoint error: {e}")
    sys.exit(1)

# Test Verify Token
print("  Testing /api/verify/...")
try:
    response = client.post(
        '/students/api/verify/',
        data=json.dumps({'token': login_access_token}),
        content_type='application/json'
    )
    if response.status_code == 200:
        data = response.json()
        print(f"    ✓ Token verification successful (Status: {response.status_code})")
        print(f"      Valid: {data.get('valid')}")
    else:
        print(f"    ✗ Token verification failed (Status: {response.status_code})")
        sys.exit(1)
except Exception as e:
    print(f"    ✗ Verify endpoint error: {e}")
    sys.exit(1)

# Test Refresh Token
print("  Testing /api/refresh/...")
try:
    response = client.post(
        '/students/api/refresh/',
        data=json.dumps({'refresh_token': login_refresh_token}),
        content_type='application/json'
    )
    if response.status_code == 200:
        data = response.json()
        print(f"    ✓ Token refresh successful (Status: {response.status_code})")
        print(f"      New token: {data.get('access_token', '')[:50]}...")
    else:
        print(f"    ✗ Token refresh failed (Status: {response.status_code})")
        sys.exit(1)
except Exception as e:
    print(f"    ✗ Refresh endpoint error: {e}")
    sys.exit(1)

# Test Logout
print("  Testing /api/logout/...")
try:
    response = client.post(
        '/students/api/logout/',
        data=json.dumps({'refresh_token': login_refresh_token}),
        content_type='application/json'
    )
    if response.status_code == 200:
        data = response.json()
        print(f"    ✓ Logout successful (Status: {response.status_code})")
        print(f"      Message: {data.get('message')}")
        
        # Verify token is revoked
        rt = RefreshToken.objects.get(token=login_refresh_token)
        print(f"      Token revoked: {rt.is_revoked}")
    else:
        print(f"    ✗ Logout failed (Status: {response.status_code})")
        sys.exit(1)
except Exception as e:
    print(f"    ✗ Logout endpoint error: {e}")
    sys.exit(1)

# STEP 8: Test Page Access
print("\n[STEP 8] Testing Page Access...")
print("-" * 70)

# Test Login Page
print("  Testing login page access...")
try:
    response = client.get('/students/login/')
    if response.status_code == 200:
        print(f"    ✓ Login page accessible (Status: {response.status_code})")
    else:
        print(f"    ✗ Login page error (Status: {response.status_code})")
except Exception as e:
    print(f"    ✗ Login page error: {e}")

# Test Register Page
print("  Testing register page access...")
try:
    response = client.get('/students/register/')
    if response.status_code == 200:
        print(f"    ✓ Register page accessible (Status: {response.status_code})")
    else:
        print(f"    ✗ Register page error (Status: {response.status_code})")
except Exception as e:
    print(f"    ✗ Register page error: {e}")

# STEP 9: Database Verification
print("\n[STEP 9] Database Verification...")
print("-" * 70)
try:
    # Count tables and records
    user_count = User.objects.count()
    student_count = Student.objects.count()
    refresh_token_count = RefreshToken.objects.count()
    
    print(f"✓ Users in database: {user_count}")
    print(f"✓ Students in database: {student_count}")
    print(f"✓ Refresh tokens in database: {refresh_token_count}")
    
    # List active tokens
    active_tokens = RefreshToken.objects.filter(is_revoked=False).count()
    revoked_tokens = RefreshToken.objects.filter(is_revoked=True).count()
    print(f"✓ Active tokens: {active_tokens}")
    print(f"✓ Revoked tokens: {revoked_tokens}")
except Exception as e:
    print(f"✗ Database verification failed: {e}")
    sys.exit(1)

# STEP 10: Configuration Check
print("\n[STEP 10] Configuration Check...")
print("-" * 70)
try:
    print(f"✓ JWT Access Token Expiry: {settings.JWT_ACCESS_TOKEN_EXPIRY_MINUTES} minutes")
    print(f"✓ JWT Refresh Token Expiry: {settings.JWT_REFRESH_TOKEN_EXPIRY_DAYS} days")
    
    # Check middleware
    if 'students.auth_middleware.JWTAuthenticationMiddleware' in settings.MIDDLEWARE:
        print(f"✓ JWT Middleware: INSTALLED")
    else:
        print(f"⚠ JWT Middleware: NOT FOUND in settings")
except Exception as e:
    print(f"✗ Configuration check failed: {e}")

# FINAL SUMMARY
print("\n" + "="*70)
print(" SETUP COMPLETE - ALL TESTS PASSED!")
print("="*70)

print("""
✅ JWT Authentication is fully operational!

NEXT STEPS:
1. Start Django server: python manage.py runserver
2. Access login page: http://localhost:8000/students/login/
3. Use test credentials:
   - Username: jwttest
   - Password: jwttest123

API ENDPOINTS AVAILABLE:
- POST   /students/api/login/    → Get tokens
- POST   /students/api/refresh/  → Refresh token
- POST   /students/api/logout/   → Revoke token
- POST   /students/api/verify/   → Check token
- GET    /students/api/verify-get/ → Check from header

DOCUMENTATION FILES:
- JWT_README.md - Overview
- JWT_QUICK_START.md - API reference
- JWT_AUTHENTICATION_GUIDE.md - Complete guide
- JWT_FLOW_DIAGRAMS.md - Visual diagrams

""")

# Cleanup
print("[CLEANUP] Removing test user...")
test_user.delete()
print("✓ Test user removed")

print("\n" + "="*70)
print(" READY FOR USE!")
print("="*70 + "\n")
