"""
Test script to verify Phase 1C + 1D integration
Tests all API endpoints and verifies backend is working correctly
"""

import httpx
import sys
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

def print_test(test_name: str, passed: bool, details: str = ""):
    """Print test result with color"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} | {test_name}")
    if details:
        print(f"     {details}")

def test_health_check():
    """Test health check endpoint"""
    try:
        response = httpx.get(f"{BASE_URL}/health", timeout=5.0)
        passed = response.status_code == 200 and response.json().get("status") == "healthy"
        print_test("Health Check", passed, f"Status: {response.status_code}")
        return passed
    except Exception as e:
        print_test("Health Check", False, f"Error: {str(e)}")
        return False

def test_stats_endpoint():
    """Test stats endpoint"""
    try:
        response = httpx.get(f"{API_V1}/stats", timeout=5.0)
        passed = response.status_code == 200
        data = response.json()
        print_test("Stats Endpoint", passed, f"Total resumes: {data.get('total_resumes', 0)}")
        return passed
    except Exception as e:
        print_test("Stats Endpoint", False, f"Error: {str(e)}")
        return False

def test_analytics_dashboard():
    """Test analytics dashboard endpoint"""
    try:
        response = httpx.get(f"{API_V1}/analytics/dashboard", timeout=5.0)
        passed = response.status_code == 200
        data = response.json()
        print_test("Analytics Dashboard", passed, 
                  f"Total matches: {data.get('total_matches', 0)}")
        return passed
    except Exception as e:
        print_test("Analytics Dashboard", False, f"Error: {str(e)}")
        return False

def test_jobs_list():
    """Test jobs list endpoint"""
    try:
        response = httpx.get(f"{API_V1}/jobs/", timeout=5.0)
        passed = response.status_code == 200
        jobs = response.json()
        print_test("Jobs List", passed, f"Found {len(jobs)} jobs")
        return passed
    except Exception as e:
        print_test("Jobs List", False, f"Error: {str(e)}")
        return False

def test_candidates_list():
    """Test candidates list endpoint"""
    try:
        response = httpx.get(f"{API_V1}/candidates/", timeout=5.0)
        passed = response.status_code == 200
        data = response.json()
        count = data.get('total', 0) if isinstance(data, dict) else len(data)
        print_test("Candidates List", passed, f"Found {count} candidates")
        return passed
    except Exception as e:
        print_test("Candidates List", False, f"Error: {str(e)}")
        return False

def test_matches_list():
    """Test matches list endpoint"""
    try:
        response = httpx.get(f"{API_V1}/matches/", timeout=5.0)
        passed = response.status_code == 200
        matches = response.json()
        print_test("Matches List", passed, f"Found {len(matches)} matches")
        return passed
    except Exception as e:
        print_test("Matches List", False, f"Error: {str(e)}")
        return False

def test_interviews_list():
    """Test interviews list endpoint"""
    try:
        response = httpx.get(f"{API_V1}/interviews/", timeout=5.0)
        passed = response.status_code == 200
        interviews = response.json()
        print_test("Interviews List", passed, f"Found {len(interviews)} interviews")
        return passed
    except Exception as e:
        print_test("Interviews List", False, f"Error: {str(e)}")
        return False

def test_skills_list():
    """Test skills list endpoint"""
    try:
        response = httpx.get(f"{API_V1}/skills/", timeout=5.0)
        passed = response.status_code == 200
        skills = response.json()
        print_test("Skills List", passed, f"Found {len(skills)} skills")
        return passed
    except Exception as e:
        print_test("Skills List", False, f"Error: {str(e)}")
        return False

def test_skills_top():
    """Test top skills endpoint"""
    try:
        response = httpx.get(f"{API_V1}/skills/top?n=5", timeout=5.0)
        passed = response.status_code == 200
        skills = response.json()
        print_test("Top Skills", passed, f"Found {len(skills)} top skills")
        return passed
    except Exception as e:
        print_test("Top Skills", False, f"Error: {str(e)}")
        return False

def test_create_job():
    """Test job creation"""
    try:
        job_data = {
            "title": "Test Job - Senior Python Developer",
            "description": "Looking for an experienced Python developer with FastAPI and ML experience",
            "required_skills": ["Python", "FastAPI", "Machine Learning"],
            "experience_years": 5,
            "status": "active"
        }
        response = httpx.post(f"{API_V1}/jobs/", json=job_data, timeout=5.0)
        passed = response.status_code in [200, 201]
        job = response.json() if passed else {}
        print_test("Create Job", passed, f"Job ID: {job.get('id', 'N/A')}")
        return passed, job.get('id')
    except Exception as e:
        print_test("Create Job", False, f"Error: {str(e)}")
        return False, None

def test_upload_resume():
    """Test resume upload (requires a sample file)"""
    sample_resume = Path("data/sample_resumes/john_doe_simple.txt")
    if not sample_resume.exists():
        print_test("Upload Resume", False, "Sample resume not found - skipping")
        return False, None
    
    try:
        with open(sample_resume, "rb") as f:
            files = {"file": (sample_resume.name, f, "text/plain")}
            response = httpx.post(f"{API_V1}/resumes/upload", files=files, timeout=10.0)
        
        passed = response.status_code in [200, 201]
        resume = response.json() if passed else {}
        print_test("Upload Resume", passed, f"Resume ID: {resume.get('id', 'N/A')}")
        return passed, resume.get('id')
    except Exception as e:
        print_test("Upload Resume", False, f"Error: {str(e)}")
        return False, None

def run_all_tests():
    """Run all integration tests"""
    print("=" * 70)
    print("Phase 1C + 1D Integration Tests")
    print("=" * 70)
    print()
    
    # Check if server is running
    print("🔍 Checking if backend server is running...")
    try:
        httpx.get(BASE_URL, timeout=3.0)
        print("✅ Backend server is reachable")
        print()
    except:
        print("❌ ERROR: Backend server is not running!")
        print("   Please start the server with: python src/api/main.py")
        print()
        sys.exit(1)
    
    # Run tests
    print("📋 Running API Tests...")
    print("-" * 70)
    
    results = []
    
    # Core endpoints
    results.append(("Health Check", test_health_check()))
    results.append(("Stats", test_stats_endpoint()))
    results.append(("Analytics", test_analytics_dashboard()))
    
    # List endpoints
    results.append(("Jobs List", test_jobs_list()))
    results.append(("Candidates List", test_candidates_list()))
    results.append(("Matches List", test_matches_list()))
    results.append(("Interviews List", test_interviews_list()))
    results.append(("Skills List", test_skills_list()))
    results.append(("Top Skills", test_skills_top()))
    
    # Create operations (optional)
    print()
    print("📝 Testing Create Operations...")
    print("-" * 70)
    job_created, job_id = test_create_job()
    results.append(("Create Job", job_created))
    
    resume_created, resume_id = test_upload_resume()
    results.append(("Upload Resume", resume_created))
    
    # Summary
    print()
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"Tests Passed: {passed}/{total} ({percentage:.1f}%)")
    print()
    
    if passed == total:
        print("🎉 All tests passed! Backend is working correctly!")
        print()
        print("Next steps:")
        print("  1. Start the frontend: cd frontend && npm run dev")
        print("  2. Open browser: http://localhost:5173")
        print("  3. Test full integration from UI")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print()
        failed_tests = [name for name, result in results if not result]
        print("Failed tests:")
        for test_name in failed_tests:
            print(f"  - {test_name}")
    
    print()
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
