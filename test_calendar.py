#!/usr/bin/env python
"""Test script to verify calendar functionality."""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from students.models import Student

User = get_user_model()

print("=" * 80)
print("CALENDAR FUNCTIONALITY TEST")
print("=" * 80)

# Create test client
client = Client()

# Check if there are any students
student_count = Student.objects.count()
print(f"\n✓ Total students in database: {student_count}")

# Test 1: Check if calendar URL is accessible without login
print("\n[TEST 1] Check calendar URL (should redirect to login if not authenticated)...")
response = client.get('/students/calendar/')
print(f"  Status code: {response.status_code}")
if response.status_code == 302:
    print("  ✓ Correctly redirects to login when not authenticated")
else:
    print(f"  ✗ Unexpected status code: {response.status_code}")

# Test 2: Create a test user and login
print("\n[TEST 2] Create test user and login...")
try:
    test_user = User.objects.create_user(
        username='testuser123',
        email='testuser@example.com',
        password='testpass123'
    )
    print(f"  ✓ Created test user: {test_user.username}")
except Exception as e:
    test_user = User.objects.get(username='testuser123')
    print(f"  ✓ Test user already exists: {test_user.username}")

# Login
login_success = client.login(username='testuser123', password='testpass123')
print(f"  ✓ Login status: {login_success}")

# Test 3: Access calendar page
print("\n[TEST 3] Access calendar page as authenticated user...")
response = client.get('/students/calendar/')
print(f"  Status code: {response.status_code}")
if response.status_code == 200:
    print("  ✓ Calendar page loaded successfully!")
    if b'Registration Calendar' in response.content:
        print("  ✓ Calendar title found in response")
    if b'calendar-grid' in response.content:
        print("  ✓ Calendar grid element found in response")
else:
    print(f"  ✗ Failed to load calendar page: {response.status_code}")
    print(f"  Response content preview: {response.content[:200]}")

# Test 4: Check API endpoint for calendar data
print("\n[TEST 4] Test calendar data API endpoint...")
response = client.get('/students/api/calendar-data/?year=2024&month=6')
print(f"  Status code: {response.status_code}")
if response.status_code == 200:
    print("  ✓ Calendar API endpoint responding")
    data = response.json()
    if 'days' in data:
        print(f"  ✓ Calendar days in response: {len(data['days'])} weeks")
    if 'total_registrations' in data:
        print(f"  ✓ Total registrations in month: {data['total_registrations']}")
else:
    print(f"  ✗ API endpoint failed: {response.status_code}")

# Test 5: Check student count API
print("\n[TEST 5] Test student count API endpoint...")
response = client.get('/students/api/student-count/')
print(f"  Status code: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"  ✓ Student count API responding")
    print(f"  ✓ Total students (from API): {data.get('count', 'N/A')}")
else:
    print(f"  ✗ API endpoint failed: {response.status_code}")

print("\n" + "=" * 80)
print("TEST COMPLETED")
print("=" * 80)
print("\nIf all tests passed, the calendar should be visible:")
print("  1. Go to: http://localhost:8000/students/dashboard/")
print("  2. Login with your credentials")
print("  3. Look for 'Calendar' in the navigation bar")
print("  4. Click 'Calendar' dropdown or 'View Full Calendar'")
print("=" * 80)
