"""
Test script for JWT authentication.
Run this script to verify JWT authentication is working correctly.
"""
import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from students.models import RefreshToken
from students.jwt_utils import JWTHandler
from django.conf import settings

# Initialize client
client = Client()

print("=" * 60)
print("JWT Authentication Testing")
print("=" * 60)

# Test 1: JWT Token Generation
print("\n[TEST 1] JWT Token Generation")
print("-" * 60)
jwt_handler = JWTHandler(settings.SECRET_KEY)
test_token = jwt_handler.generate_access_token(1, 'testuser')
print(f"✓ Generated access token: {test_token[:50]}...")
print(f"  Token length: {len(test_token)} characters")

# Test 2: Token Verification
print("\n[TEST 2] Token Verification")
print("-" * 60)
is_valid, payload = jwt_handler.verify_token(test_token)
print(f"✓ Token is valid: {is_valid}")
if payload:
    print(f"  Payload: {json.dumps(payload, indent=2)}")

# Test 3: Invalid Token
print("\n[TEST 3] Invalid Token Handling")
print("-" * 60)
invalid_token = "invalid.token.here"
is_valid, payload = jwt_handler.verify_token(invalid_token)
print(f"✓ Invalid token detected: {not is_valid}")

# Test 4: Create test user
print("\n[TEST 4] Create Test User")
print("-" * 60)
# Clean up first
User.objects.filter(username='jwttest').delete()
test_user = User.objects.create_user(
    username='jwttest',
    password='testpass123',
    email='jwttest@test.com',
    first_name='JWT',
    last_name='Tester'
)
print(f"✓ Created test user: {test_user.username}")

# Test 5: API Login
print("\n[TEST 5] API Login Endpoint")
print("-" * 60)
response = client.post(
    '/students/api/login/',
    data=json.dumps({'username': 'jwttest', 'password': 'testpass123'}),
    content_type='application/json'
)
print(f"✓ Response status: {response.status_code}")
data = response.json()
if response.status_code == 200:
    print(f"  User ID: {data.get('user_id')}")
    print(f"  Username: {data.get('username')}")
    print(f"  Access token: {data.get('access_token', '')[:50]}...")
    print(f"  Refresh token: {data.get('refresh_token', '')[:50]}...")
    access_token = data.get('access_token')
    refresh_token = data.get('refresh_token')
else:
    print(f"  Error: {data}")

# Test 6: Verify Token Endpoint
print("\n[TEST 6] Token Verification Endpoint")
print("-" * 60)
response = client.post(
    '/students/api/verify/',
    data=json.dumps({'token': access_token}),
    content_type='application/json'
)
print(f"✓ Response status: {response.status_code}")
data = response.json()
print(f"  Valid: {data.get('valid')}")
if data.get('valid'):
    print(f"  User ID: {data.get('user_id')}")
    print(f"  Username: {data.get('username')}")

# Test 7: Refresh Token Endpoint
print("\n[TEST 7] Token Refresh Endpoint")
print("-" * 60)
response = client.post(
    '/students/api/refresh/',
    data=json.dumps({'refresh_token': refresh_token}),
    content_type='application/json'
)
print(f"✓ Response status: {response.status_code}")
data = response.json()
if response.status_code == 200:
    print(f"  New access token: {data.get('access_token', '')[:50]}...")
    new_access_token = data.get('access_token')
else:
    print(f"  Error: {data}")

# Test 8: Logout Endpoint
print("\n[TEST 8] Logout Endpoint")
print("-" * 60)
response = client.post(
    '/students/api/logout/',
    data=json.dumps({'refresh_token': refresh_token}),
    content_type='application/json'
)
print(f"✓ Response status: {response.status_code}")
data = response.json()
print(f"  Message: {data.get('message', 'Logged out successfully')}")

# Verify refresh token is revoked
refresh_token_obj = RefreshToken.objects.get(token=refresh_token)
print(f"  Refresh token revoked: {refresh_token_obj.is_revoked}")

# Test 9: RefreshToken Model
print("\n[TEST 9] RefreshToken Model")
print("-" * 60)
refresh_tokens = RefreshToken.objects.filter(user=test_user)
print(f"✓ Refresh tokens for user: {refresh_tokens.count()}")
for rt in refresh_tokens:
    print(f"  - Token ID: {rt.id}")
    print(f"    Revoked: {rt.is_revoked}")
    print(f"    Expired: {rt.is_expired()}")
    print(f"    Valid: {rt.is_valid()}")

# Test 10: Authorization Header
print("\n[TEST 10] Authorization Header in API Request")
print("-" * 60)
# First get a fresh token
response = client.post(
    '/students/api/login/',
    data=json.dumps({'username': 'jwttest', 'password': 'testpass123'}),
    content_type='application/json'
)
token = response.json().get('access_token')

response = client.get(
    '/students/api/verify-get/',
    HTTP_AUTHORIZATION=f'Bearer {token}'
)
print(f"✓ Response status: {response.status_code}")
data = response.json()
print(f"  Valid: {data.get('valid')}")
if data.get('valid'):
    print(f"  User ID: {data.get('user_id')}")

print("\n" + "=" * 60)
print("All JWT Authentication Tests Completed!")
print("=" * 60)

# Cleanup
print("\nCleaning up test user...")
test_user.delete()
print("✓ Test user deleted")
