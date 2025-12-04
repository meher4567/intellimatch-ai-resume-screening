"""
Setup script to activate jobs and generate matches for better testing
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def activate_jobs():
    """Activate all open jobs"""
    print("\n🔄 Step 1: Activating Jobs...")
    
    # Get all jobs
    response = requests.get(f"{BASE_URL}/api/v1/jobs/")
    jobs = response.json()
    
    activated = 0
    for job in jobs:
        if job['status'] in ['open', 'draft']:
            # Update job to active
            update_data = {**job, 'status': 'active'}
            try:
                requests.put(f"{BASE_URL}/api/v1/jobs/{job['id']}", json=update_data)
                print(f"  ✅ Activated: {job['title']}")
                activated += 1
            except Exception as e:
                print(f"  ❌ Failed to activate {job['title']}: {e}")
    
    print(f"\n✅ Activated {activated} jobs")
    return activated

def generate_matches():
    """Generate matches for all active jobs"""
    print("\n🔄 Step 2: Generating Matches...")
    
    # Get all jobs
    response = requests.get(f"{BASE_URL}/api/v1/jobs/")
    jobs = response.json()
    
    total_matches = 0
    for job in jobs:
        if job['status'] == 'active':
            try:
                # Get matches for this job
                response = requests.get(
                    f"{BASE_URL}/api/v1/matching/{job['id']}",
                    params={'top_k': 10, 'include_explanation': True}
                )
                
                if response.status_code == 200:
                    matches = response.json()
                    print(f"  ✅ {job['title']}: Found {len(matches)} matches")
                    total_matches += len(matches)
                else:
                    print(f"  ⚠️  {job['title']}: No matches found")
                    
            except Exception as e:
                print(f"  ❌ Error matching {job['title']}: {e}")
    
    print(f"\n✅ Generated {total_matches} total matches")
    return total_matches

def check_system_ready():
    """Verify system is ready"""
    print("\n🔄 Step 3: Verifying System...")
    
    try:
        # Check stats
        response = requests.get(f"{BASE_URL}/api/v1/analytics/stats")
        stats = response.json()
        
        print(f"\n📊 Final Status:")
        print(f"  📄 Resumes: {stats['total_resumes']}")
        print(f"  💼 Total Jobs: {stats['total_jobs']}")
        print(f"  ✅ Active Jobs: {stats['active_jobs']}")
        print(f"  🔗 Matches: {stats['total_matches']}")
        
        if stats['active_jobs'] > 0 and stats['total_matches'] > 0:
            print(f"\n✨ System is ready! Open http://localhost:3000 to test")
            return True
        else:
            print(f"\n⚠️  System needs more data")
            return False
            
    except Exception as e:
        print(f"❌ Error checking system: {e}")
        return False

def main():
    print("="*60)
    print("🚀 IntelliMatch AI - System Setup")
    print("="*60)
    
    try:
        # Step 1: Activate jobs
        activated = activate_jobs()
        
        # Step 2: Generate matches
        if activated > 0:
            matches = generate_matches()
        
        # Step 3: Verify
        ready = check_system_ready()
        
        print("\n" + "="*60)
        if ready:
            print("✅ Setup Complete! System is ready to use.")
            print("\n📝 Next Steps:")
            print("  1. Open http://localhost:3000 in your browser")
            print("  2. Navigate to Dashboard to see stats")
            print("  3. Go to Jobs page to view active jobs")
            print("  4. Check Candidates page for matches")
            print("  5. Try uploading more resumes")
        else:
            print("⚠️  Setup incomplete. Check errors above.")
        print("="*60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Backend server is not running!")
        print("   Please start the backend:")
        print("   python -m uvicorn src.main:app --reload --port 8000\n")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")

if __name__ == "__main__":
    main()
