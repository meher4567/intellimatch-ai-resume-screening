"""
Quick health check for IntelliMatch API
Usage: python check_health.py
"""

import httpx
import sys

def check_health():
    try:
        response = httpx.get("http://localhost:8000/health", timeout=5.0)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend is HEALTHY")
            print(f"   Status: {data.get('status')}")
            print(f"   Environment: {data.get('environment')}")
            print(f"   Version: {data.get('version')}")
            print(f"\n   Services:")
            services = data.get('services', {})
            for service, status in services.items():
                icon = "✅" if status == "up" else "❌"
                print(f"   {icon} {service}: {status}")
            return True
        else:
            print(f"❌ Backend returned status code: {response.status_code}")
            return False
            
    except httpx.ConnectError:
        print("❌ Backend is NOT RUNNING")
        print("   Start it with: python src/api/main.py")
        return False
    except Exception as e:
        print(f"❌ Error checking health: {e}")
        return False

if __name__ == "__main__":
    success = check_health()
    sys.exit(0 if success else 1)
