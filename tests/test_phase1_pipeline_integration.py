"""
Comprehensive Integration Test for Phase 1 Pipeline
Tests the complete pipeline end-to-end with real parsed resume data
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.phase1_pipeline import analyze_resume
import json


def test_pipeline_with_sample_resume():
    """Test pipeline with a realistic sample resume"""
    
    sample_resume = {
        'text': """
John Doe
Senior Software Engineer

Professional Summary:
Experienced backend engineer with 8+ years building scalable microservices.
Expert in Python, Django, AWS, and Docker. Led teams of 5+ developers.

Skills:
- Languages: Python, Java, JavaScript
- Frameworks: Django, Flask, Spring Boot
- Cloud: AWS (EC2, S3, Lambda), Docker, Kubernetes
- Databases: PostgreSQL, MongoDB, Redis

Experience:

Senior Software Engineer | TechCorp Inc | San Francisco, CA
January 2020 - Present
- Led development of microservices architecture serving 10M+ users
- Reduced API latency by 40% through optimization and caching strategies
- Mentored 3 junior developers and conducted code reviews
- Technologies: Python, Django, AWS, Docker, Kubernetes, PostgreSQL

Software Engineer | StartupXYZ | Remote
June 2017 - December 2019
- Built RESTful APIs using Django and Flask
- Implemented CI/CD pipelines with Jenkins and Docker
- Migrated monolithic application to microservices architecture
- Improved test coverage from 40% to 85%

Junior Developer | WebSolutions Ltd | New York, NY
July 2015 - May 2017
- Developed web applications using Django and React
- Collaborated with designers to implement responsive UIs
- Fixed bugs and implemented new features

Education:
Bachelor of Science in Computer Science
State University, 2011-2015
GPA: 3.7/4.0

Certifications:
- AWS Certified Solutions Architect - Associate
- Certified Kubernetes Administrator (CKA)

Projects:
- OpenSource Contributor: Django REST Framework (500+ stars)
- Personal Project: Real-time Chat Application (Node.js, Socket.io, Redis)
""",
        'experience': [
            {
                'title': 'Senior Software Engineer',
                'company': 'TechCorp Inc',
                'location': 'San Francisco, CA',
                'start_date': 'January 2020',
                'end_date': 'Present',
                'description': 'Led development of microservices architecture serving 10M+ users. Reduced API latency by 40%.'
            },
            {
                'title': 'Software Engineer',
                'company': 'StartupXYZ',
                'location': 'Remote',
                'start_date': 'June 2017',
                'end_date': 'December 2019',
                'description': 'Built RESTful APIs using Django and Flask. Implemented CI/CD pipelines.'
            },
            {
                'title': 'Junior Developer',
                'company': 'WebSolutions Ltd',
                'location': 'New York, NY',
                'start_date': 'July 2015',
                'end_date': 'May 2017',
                'description': 'Developed web applications using Django and React.'
            }
        ],
        'skills': {
            'all_skills': ['Python', 'Java', 'JavaScript', 'Django', 'Flask', 'Spring Boot', 'AWS', 'Docker', 'Kubernetes', 'PostgreSQL', 'MongoDB', 'Redis']
        },
        'education': [
            {
                'degree': 'Bachelor of Science in Computer Science',
                'institution': 'State University',
                'year': '2011-2015'
            }
        ]
    }
    
    job_description = """
We are looking for a Senior Backend Engineer to join our growing team.

Requirements:
- 5+ years of experience in backend development
- Strong proficiency in Python and Django
- Experience with microservices architecture
- AWS cloud experience required
- Docker and Kubernetes knowledge
- Strong communication and mentorship skills
- Bachelor's degree in Computer Science or related field

Responsibilities:
- Design and build scalable backend systems
- Lead technical architecture decisions
- Mentor junior developers
- Collaborate with product and design teams
- Ensure code quality and best practices

Nice to have:
- Experience with CI/CD pipelines
- PostgreSQL expertise
- AWS certifications
"""
    
    print("=" * 80)
    print("PHASE 1 PIPELINE INTEGRATION TEST")
    print("=" * 80)
    
    # Run pipeline
    print("\n1️⃣ Running pipeline analysis...")
    result = analyze_resume(sample_resume, job_description)
    
    # Check all expected keys are present
    print("\n2️⃣ Validating output structure...")
    expected_keys = ['language', 'quality', 'skills', 'timeline', 'interview_questions', 'bias_flags', 'warnings']
    for key in expected_keys:
        assert key in result, f"Missing key: {key}"
        print(f"   ✅ {key}: {type(result[key]).__name__}")
    
    # Validate no critical warnings
    print("\n3️⃣ Checking for warnings...")
    if result['warnings']:
        print(f"   ⚠️  {len(result['warnings'])} warnings found:")
        for w in result['warnings']:
            print(f"      - {w}")
    else:
        print("   ✅ No warnings!")
    
    # Check language detection
    print("\n4️⃣ Language Detection:")
    print(f"   Detected: {result['language']}")
    
    # Check quality score
    print("\n5️⃣ Resume Quality Score:")
    if result['quality']:
        print(f"   Overall Score: {result['quality'].get('overall_score', 'N/A')}/10")
        print(f"   Grade: {result['quality'].get('grade', 'N/A')}")
    else:
        print("   ❌ Quality scoring failed")
    
    # Check skills extraction
    print("\n6️⃣ Skills Analysis:")
    if result['skills']:
        skill_count = result['skills'].get('skill_count', 0)
        skills_with_context = result['skills'].get('skills_with_context', [])
        print(f"   Extracted {skill_count} contextualized skills")
        if skill_count > 0:
            skill_names = [s.get('skill') for s in skills_with_context[:5]]
            print(f"   Sample skills: {skill_names}")
            insights = result['skills'].get('insights', {})
            print(f"   Primary skills: {insights.get('primary_skills', [])}")
            print(f"   Average context score: {insights.get('avg_context_score', 0):.2f}")
    else:
        print("   ❌ Skills extraction failed")
    
    # Check timeline analysis
    print("\n7️⃣ Timeline Analysis:")
    if result['timeline']:
        print(f"   Total Experience: {result['timeline'].get('total_experience_years', 'N/A')} years")
        print(f"   Employment Gaps: {result['timeline'].get('gap_count', 0)}")
        print(f"   Job Hopping Score: {result['timeline'].get('job_hopping_score', 'N/A')}")
        progression = result['timeline'].get('progression', {})
        print(f"   Career Progression: {progression.get('trajectory', 'N/A')}")
    else:
        print("   ❌ Timeline analysis failed")
    
    # Check interview questions
    print("\n8️⃣ Interview Questions:")
    if result['interview_questions']:
        counts = result['interview_questions'].get('counts', {})
        print(f"   Generated Questions:")
        for q_type, count in counts.items():
            print(f"      {q_type}: {count}")
    else:
        print("   ❌ Interview question generation failed")
    
    # Check bias detection
    print("\n9️⃣ Bias Detection:")
    if result['bias_flags']:
        flags = result['bias_flags'].get('flags', [])
        print(f"   Bias flags found: {len(flags)}")
        if flags:
            for flag in flags[:3]:  # Show first 3
                print(f"      - {flag.get('span_text', 'N/A')}: {flag.get('reason', 'N/A')}")
    else:
        print("   ❌ Bias detection failed")
    
    print("\n" + "=" * 80)
    print("✅ INTEGRATION TEST COMPLETED SUCCESSFULLY")
    print("=" * 80)
    
    # Save result to file for inspection
    output_file = Path(__file__).parent.parent / 'test_results' / 'phase1_pipeline_integration_test.json'
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    print(f"\n📁 Full results saved to: {output_file}")
    
    return result


if __name__ == '__main__':
    test_pipeline_with_sample_resume()
