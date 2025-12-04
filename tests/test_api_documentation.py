"""
Test OpenAPI documentation enhancements
Verifies Swagger UI and ReDoc are working with enhanced examples
"""
import requests

BASE_URL = "http://localhost:8000"

def test_openapi_docs():
    """Test OpenAPI documentation endpoints"""
    print("\n" + "="*70)
    print("📚 OPENAPI DOCUMENTATION TEST")
    print("="*70)
    
    # Test 1: Check OpenAPI JSON schema
    print("\n1️⃣  Testing OpenAPI schema endpoint...")
    response = requests.get(f"{BASE_URL}/openapi.json")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    schema = response.json()
    print(f"   ✅ OpenAPI version: {schema.get('openapi')}")
    print(f"   ✅ API title: {schema['info']['title']}")
    print(f"   ✅ API version: {schema['info']['version']}")
    
    # Check for enhanced metadata
    assert 'contact' in schema['info'], "Missing contact info"
    assert 'license' in schema['info'], "Missing license info"
    print(f"   ✅ Contact: {schema['info']['contact'].get('email')}")
    print(f"   ✅ License: {schema['info']['license'].get('name')}")
    
    # Test 2: Check for tags
    print("\n2️⃣  Checking API tags...")
    tags = schema.get('tags', [])
    tag_names = [tag['name'] for tag in tags]
    print(f"   Found {len(tags)} tags: {', '.join(tag_names)}")
    
    expected_tags = ['Authentication', 'Resumes', 'Jobs', 'Matches', 'Candidates', 'Analytics']
    for tag in expected_tags:
        assert tag in tag_names, f"Missing tag: {tag}"
    print(f"   ✅ All expected tags present")
    
    # Test 3: Check for enhanced endpoint examples
    print("\n3️⃣  Checking endpoint examples...")
    paths = schema.get('paths', {})
    
    examples_found = 0
    for path, methods in paths.items():
        for method, details in methods.items():
            if 'responses' in details:
                for status_code, response_details in details['responses'].items():
                    if 'content' in response_details:
                        for content_type, content_details in response_details['content'].items():
                            if 'example' in content_details:
                                examples_found += 1
    
    print(f"   ✅ Found {examples_found} endpoint examples")
    assert examples_found > 0, "No examples found in OpenAPI schema"
    
    # Test 4: Check specific endpoints have examples
    print("\n4️⃣  Verifying key endpoints have examples...")
    
    key_endpoints = [
        ("/api/v1/jobs", "post"),
        ("/api/v1/matches/find", "post"),
        ("/api/v1/candidates/", "get"),
    ]
    
    for endpoint, method in key_endpoints:
        if endpoint in paths and method in paths[endpoint]:
            endpoint_data = paths[endpoint][method]
            has_examples = any(
                'example' in resp.get('content', {}).get('application/json', {})
                for resp in endpoint_data.get('responses', {}).values()
            )
            status = "✅" if has_examples else "⚠️"
            print(f"   {status} {method.upper()} {endpoint}: {'Has examples' if has_examples else 'No examples'}")
    
    # Test 5: Verify Swagger UI is accessible
    print("\n5️⃣  Checking Swagger UI...")
    response = requests.get(f"{BASE_URL}/docs")
    assert response.status_code == 200, f"Swagger UI not accessible: {response.status_code}"
    assert "swagger" in response.text.lower(), "Swagger UI not properly rendered"
    print(f"   ✅ Swagger UI accessible at {BASE_URL}/docs")
    
    # Test 6: Verify ReDoc is accessible
    print("\n6️⃣  Checking ReDoc...")
    response = requests.get(f"{BASE_URL}/redoc")
    assert response.status_code == 200, f"ReDoc not accessible: {response.status_code}"
    assert "redoc" in response.text.lower(), "ReDoc not properly rendered"
    print(f"   ✅ ReDoc accessible at {BASE_URL}/redoc")
    
    print("\n" + "="*70)
    print("✅ ALL DOCUMENTATION TESTS PASSED")
    print("="*70)
    print(f"\n📖 View API Documentation:")
    print(f"   • Swagger UI: {BASE_URL}/docs")
    print(f"   • ReDoc: {BASE_URL}/redoc")
    print(f"   • OpenAPI JSON: {BASE_URL}/openapi.json")
    print(f"\n🎯 Enhanced Features:")
    print(f"   • Contact information added")
    print(f"   • License information added")
    print(f"   • {len(tags)} organized API tags")
    print(f"   • {examples_found} endpoint examples")
    print(f"   • Detailed parameter descriptions")
    print(f"   • Response schema examples")


if __name__ == "__main__":
    try:
        test_openapi_docs()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Server not running")
        print(f"   Start server: uvicorn src.main:app --reload")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
