"""
Upload sample resumes and jobs to the database via API
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/v1"

# Sample resumes
sample_resumes = [
    {
        "candidate_name": "Alice Johnson",
        "email": "alice.johnson@email.com",
        "phone": "+1-555-0101",
        "skills": ["Python", "Django", "PostgreSQL", "AWS", "Docker", "Kubernetes"],
        "experience_level": "senior",
        "years_of_experience": 7,
        "raw_text": "Senior Software Engineer with 7 years of experience building scalable web applications. Expert in Python, Django, and cloud technologies. Led teams of 5 developers. AWS certified.",
        "location": "San Francisco, CA"
    },
    {
        "candidate_name": "Bob Smith",
        "email": "bob.smith@email.com",
        "phone": "+1-555-0102",
        "skills": ["JavaScript", "React", "Node.js", "MongoDB", "Express"],
        "experience_level": "mid",
        "years_of_experience": 4,
        "raw_text": "Full Stack Developer with 4 years of experience in MERN stack. Built multiple e-commerce platforms. Strong problem-solving skills.",
        "location": "New York, NY"
    },
    {
        "candidate_name": "Carol Williams",
        "email": "carol.williams@email.com",
        "phone": "+1-555-0103",
        "skills": ["Java", "Spring Boot", "MySQL", "REST API", "Microservices"],
        "experience_level": "mid",
        "years_of_experience": 5,
        "raw_text": "Backend Engineer specializing in Java and Spring Boot. 5 years building microservices architectures. Experience with high-traffic systems.",
        "location": "Austin, TX"
    },
    {
        "candidate_name": "David Chen",
        "email": "david.chen@email.com",
        "phone": "+1-555-0104",
        "skills": ["Python", "Machine Learning", "TensorFlow", "PyTorch", "NLP"],
        "experience_level": "senior",
        "years_of_experience": 6,
        "raw_text": "ML Engineer with 6 years of experience in NLP and deep learning. Published researcher. Built production ML pipelines serving millions of users.",
        "location": "Seattle, WA"
    },
    {
        "candidate_name": "Emma Davis",
        "email": "emma.davis@email.com",
        "phone": "+1-555-0105",
        "skills": ["Python", "Django", "Flask", "PostgreSQL", "Redis"],
        "experience_level": "entry",
        "years_of_experience": 1,
        "raw_text": "Junior Python Developer with 1 year of experience. Recent Computer Science graduate. Internship experience at tech startup. Eager to learn.",
        "location": "Boston, MA"
    }
]

# Sample jobs
sample_jobs = [
    {
        "title": "Senior Python Engineer",
        "company": "Tech Corp",
        "description": "We're looking for a Senior Python Engineer to join our backend team. You'll work on building scalable APIs and microservices.",
        "required_skills": ["Python", "Django", "PostgreSQL", "AWS"],
        "preferred_skills": ["Docker", "Kubernetes", "Redis"],
        "min_experience_years": 5,
        "location": "San Francisco, CA",
        "salary_range": "$150,000 - $180,000",
        "status": "active"
    },
    {
        "title": "Full Stack Developer",
        "company": "Startup Inc",
        "description": "Join our fast-growing startup as a Full Stack Developer. Work with modern JavaScript frameworks and Node.js.",
        "required_skills": ["JavaScript", "React", "Node.js", "MongoDB"],
        "preferred_skills": ["TypeScript", "GraphQL", "AWS"],
        "min_experience_years": 3,
        "location": "New York, NY",
        "salary_range": "$100,000 - $130,000",
        "status": "active"
    },
    {
        "title": "ML Engineer",
        "company": "AI Solutions",
        "description": "Build production ML systems and work on cutting-edge NLP projects. Experience with transformers and large language models preferred.",
        "required_skills": ["Python", "Machine Learning", "TensorFlow", "PyTorch"],
        "preferred_skills": ["NLP", "Transformers", "AWS", "Docker"],
        "min_experience_years": 4,
        "location": "Seattle, WA",
        "salary_range": "$140,000 - $170,000",
        "status": "active"
    }
]

def upload_data():
    """Upload sample data to the API"""
    
    print("=" * 70)
    print("📤 Uploading Sample Data to IntelliMatch AI")
    print("=" * 70)
    
    # Upload resumes
    print("\n1️⃣  Uploading Resumes...")
    resume_ids = []
    for i, resume in enumerate(sample_resumes, 1):
        try:
            response = requests.post(f"{BASE_URL}/resumes/", json=resume)
            if response.status_code in [200, 201]:
                data = response.json()
                resume_id = data.get('id')
                resume_ids.append(resume_id)
                print(f"   ✅ {i}. {resume['candidate_name']} (ID: {resume_id})")
            else:
                print(f"   ❌ {i}. {resume['candidate_name']} - Error: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {i}. {resume['candidate_name']} - Error: {e}")
    
    # Upload jobs
    print("\n2️⃣  Uploading Jobs...")
    job_ids = []
    for i, job in enumerate(sample_jobs, 1):
        try:
            response = requests.post(f"{BASE_URL}/jobs/", json=job)
            if response.status_code in [200, 201]:
                data = response.json()
                job_id = data.get('id')
                job_ids.append(job_id)
                print(f"   ✅ {i}. {job['title']} at {job['company']} (ID: {job_id})")
            else:
                print(f"   ❌ {i}. {job['title']} - Error: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {i}. {job['title']} - Error: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print(f"✅ Upload Complete!")
    print(f"   Resumes: {len(resume_ids)} uploaded")
    print(f"   Jobs: {len(job_ids)} uploaded")
    print("=" * 70)
    
    return resume_ids, job_ids

if __name__ == "__main__":
    try:
        # Check if backend is running
        response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/")
        print(f"✅ Backend is running: {response.json()['message']}\n")
        
        resume_ids, job_ids = upload_data()
        
        print("\n💡 Next steps:")
        print(f"   - View resumes: http://localhost:8000/api/v1/resumes/")
        print(f"   - View jobs: http://localhost:8000/api/v1/jobs/")
        print(f"   - API docs: http://localhost:8000/docs")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Backend is not running!")
        print("   Start it with: python start_server.py")
    except Exception as e:
        print(f"❌ Error: {e}")
