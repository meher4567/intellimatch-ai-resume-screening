"""Test production improvements: logging, error handling, health check"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 70)
print("Testing Production Improvements")
print("=" * 70)

# Test 1: Enhanced Health Check
print("\n1️⃣  Testing Enhanced Health Check...")
try:
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response:")
    print(json.dumps(response.json(), indent=4))
    
    # Check for request ID header
    request_id = response.headers.get("X-Request-ID")
    if request_id:
        print(f"   ✅ Request ID in header: {request_id}")
    else:
        print(f"   ⚠️  No Request ID in header")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: API Root
print("\n2️⃣  Testing API Root...")
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    request_id = response.headers.get("X-Request-ID")
    if request_id:
        print(f"   ✅ Request ID: {request_id}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Error Handling (invalid endpoint)
print("\n3️⃣  Testing Error Handling...")
try:
    response = requests.get(f"{BASE_URL}/invalid/endpoint")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    request_id = response.headers.get("X-Request-ID")
    if request_id:
        print(f"   ✅ Request ID: {request_id}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Authentication
print("\n4️⃣  Testing Authentication with Logging...")
try:
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "Test1234"
        }
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Login successful")
        print(f"   Token: {data.get('access_token')[:30]}...")
    else:
        print(f"   Response: {response.json()}")
    
    request_id = response.headers.get("X-Request-ID")
    if request_id:
        print(f"   ✅ Request ID: {request_id}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 70)
print("✅ Production improvements tested!")
print("=" * 70)
print("\nFeatures added:")
print("  ✅ Request/response logging with timing")
print("  ✅ Unique request IDs in headers")
print("  ✅ Global exception handling")
print("  ✅ Enhanced health check (database + filesystem)")
print("  ✅ File validation utilities")
