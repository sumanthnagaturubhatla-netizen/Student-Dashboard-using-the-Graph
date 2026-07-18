#!/usr/bin/env python
"""
Diagnostic script to test calendar functionality and identify issues
"""

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
from datetime import datetime

User = get_user_model()

print("\n" + "="*80)
print("CALENDAR DIAGNOSTIC TEST")
print("="*80 + "\n")

# Create test user
try:
    test_user = User.objects.create_user(
        username='testcal123',
        email='testcal@test.com',
        password='testpass123'
    )
    print("✓ Created test user")
except:
    test_user = User.objects.get(username='testcal123')
    print("✓ Using existing test user")

# Create test client
client = Client()

print("\n" + "="*80)
print("TEST 1: Check if URL route exists")
print("="*80)

try:
    from students.urls import urlpatterns
    calendar_route = any('calendar' in str(p.pattern) for p in urlpatterns)
    if calendar_route:
        print("✓ Calendar route found in URLs")
    else:
        print("✗ Calendar route NOT found in URLs")
except Exception as e:
    print(f"✗ Error checking URL routes: {e}")

print("\n" + "="*80)
print("TEST 2: Check if calendar view exists")
print("="*80)

try:
    from students.views import calendar_view, calendar_data
    print("✓ calendar_view() exists")
    print("✓ calendar_data() exists")
except Exception as e:
    print(f"✗ Error importing views: {e}")

print("\n" + "="*80)
print("TEST 3: Check calendar template")
print("="*80)

template_path = "templates/calendar.html"
if os.path.exists(template_path):
    print(f"✓ Template exists: {template_path}")
    with open(template_path, 'r') as f:
        content = f.read()
        if 'calendarGrid' in content:
            print("✓ calendarGrid element found in template")
        else:
            print("✗ calendarGrid element NOT found in template")
else:
    print(f"✗ Template NOT found: {template_path}")

print("\n" + "="*80)
print("TEST 4: Try accessing calendar page without login")
print("="*80)

response = client.get('/students/calendar/')
print(f"Response status: {response.status_code}")
if response.status_code == 302:
    print("✓ Correctly redirects to login (expected)")
else:
    print(f"⚠ Got status {response.status_code} (expected 302)")

print("\n" + "="*80)
print("TEST 5: Login and access calendar page")
print("="*80)

login_result = client.login(username='testcal123', password='testpass123')
print(f"Login result: {login_result}")

if login_result:
    print("✓ Login successful")
    
    response = client.get('/students/calendar/')
    print(f"\nCalendar page response status: {response.status_code}")
    
    if response.status_code == 200:
        print("✓ Calendar page loads (HTTP 200)")
        
        # Check for content
        content = response.content.decode('utf-8')
        
        checks = [
            ('Registration Calendar', 'Page title'),
            ('calendarGrid', 'Calendar grid element'),
            ('calendar-grid', 'CSS class'),
            ('loadCalendar()', 'JavaScript function'),
            ('currentYear', 'Year variable'),
            ('currentMonth', 'Month variable'),
        ]
        
        for text, name in checks:
            if text in content:
                print(f"  ✓ {name} found")
            else:
                print(f"  ✗ {name} NOT found")
                
    else:
        print(f"✗ Calendar page failed with status: {response.status_code}")
        print(f"Error content: {response.content[:500]}")
else:
    print("✗ Login failed")

print("\n" + "="*80)
print("TEST 6: Test calendar API endpoint")
print("="*80)

response = client.get('/students/api/calendar-data/?year=2024&month=6')
print(f"API response status: {response.status_code}")

if response.status_code == 200:
    print("✓ API endpoint works")
    try:
        data = response.json()
        print(f"✓ JSON response valid")
        print(f"  - Year: {data.get('year')}")
        print(f"  - Month: {data.get('month_name')}")
        print(f"  - Total registrations: {data.get('total_registrations')}")
        print(f"  - Calendar weeks: {len(data.get('days', []))}")
    except Exception as e:
        print(f"✗ JSON parsing failed: {e}")
else:
    print(f"✗ API endpoint failed with status: {response.status_code}")

print("\n" + "="*80)
print("TEST 7: Check browser console errors")
print("="*80)

print("⚠ Check your browser:")
print("  1. Press: F12 (Developer Tools)")
print("  2. Go to: Console tab")
print("  3. Look for red error messages")
print("  4. Screenshot and share errors")

print("\n" + "="*80)
print("DIAGNOSTIC COMPLETE")
print("="*80 + "\n")

print("If all tests pass but calendar still doesn't open:")
print("  1. Press F12 in browser")
print("  2. Go to Console tab")
print("  3. Check for red errors")
print("  4. Share the error messages")
print("\n")
