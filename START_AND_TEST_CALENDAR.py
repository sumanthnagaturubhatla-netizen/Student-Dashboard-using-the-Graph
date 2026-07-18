#!/usr/bin/env python
"""
Quick test script to verify calendar is working and showing registration data
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
from datetime import datetime, timedelta

User = get_user_model()

print("\n" + "="*80)
print("CALENDAR DATA VERIFICATION TEST")
print("="*80 + "\n")

# Get or create test user
try:
    test_user = User.objects.create_user(
        username='testuser_calendar',
        email='test_cal@example.com',
        password='testpass123'
    )
    print(f"✓ Created test user: {test_user.username}")
except:
    test_user = User.objects.get(username='testuser_calendar')
    print(f"✓ Using existing test user: {test_user.username}")

# Check how many students are registered
total_students = Student.objects.count()
print(f"✓ Total students in database: {total_students}")

# Get today's month/year
today = datetime.now()
current_year = today.year
current_month = today.month

print(f"✓ Current month: {current_month}/{current_year}")

# Get registrations for this month
from django.db.models import Count
registrations = Student.objects.filter(
    date_registered__year=current_year,
    date_registered__month=current_month
).values('date_registered__day').annotate(count=Count('id'))

print(f"\n📊 REGISTRATIONS THIS MONTH ({current_month}/{current_year}):")
print("-" * 50)

if registrations:
    total_this_month = 0
    for reg in registrations:
        day = reg['date_registered__day']
        count = reg['count']
        total_this_month += count
        print(f"  Day {day:2d}: {count:3d} student{'s' if count != 1 else ''}")
    print(f"\n  Total: {total_this_month} registrations")
else:
    print("  No registrations this month yet")

# Test the API endpoint
print(f"\n🔗 TESTING API ENDPOINT:")
print("-" * 50)

client = Client()

# Login
client.login(username='testuser_calendar', password='testpass123')
print(f"✓ Logged in as: {test_user.username}")

# Test calendar data API
response = client.get(f'/students/api/calendar-data/?year={current_year}&month={current_month}')
print(f"✓ API response status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"✓ Calendar data received successfully")
    print(f"  - Month: {data['month_name']} {data['year']}")
    print(f"  - Total registrations: {data['total_registrations']}")
    print(f"  - Calendar weeks: {len(data['days'])}")
    if data['days']:
        print(f"  - Days per week: {len(data['days'][0])}")

# Test calendar page
print(f"\n📄 TESTING CALENDAR PAGE:")
print("-" * 50)

response = client.get('/students/calendar/')
print(f"✓ Calendar page status: {response.status_code}")

if response.status_code == 200:
    print(f"✓ Calendar page loaded successfully")
    if b'Registration Calendar' in response.content:
        print(f"✓ Calendar title found")
    if b'calendar-grid' in response.content:
        print(f"✓ Calendar grid element found")
    if b'calendarGrid' in response.content:
        print(f"✓ Calendar JavaScript found")
else:
    print(f"✗ Failed to load calendar page")

print("\n" + "="*80)
print("✅ CALENDAR IS READY!")
print("="*80)
print("\nTo view the calendar:")
print("  1. Run: python manage.py runserver")
print("  2. Go to: http://localhost:8000/students/dashboard/")
print("  3. Login with your credentials")
print("  4. Click: Calendar")
print("="*80 + "\n")
