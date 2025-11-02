"""
Test Complete Matching Pipeline with Quality Scores
Shows match score + quality score for each candidate
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.matching_engine import MatchingEngine


def test_complete_pipeline():
    """Test full matching pipeline with quality scoring"""
    
    print("=" * 90)
    print("🧪 COMPLETE MATCHING PIPELINE TEST - Match Score + Quality Score")
    print("=" * 90)
    
    # Initialize engine
    engine = MatchingEngine()
    
    # Create test resumes with varying quality
    resumes = [
        {
            'resume_id': 'excellent_candidate.pdf',
            'name': 'Alice Johnson',
            'email': 'alice@email.com',
            'phone': '555-1234',
            'linkedin': 'linkedin.com/in/alice',
            'skills': ['Python', 'Machine Learning', 'TensorFlow', 'AWS', 'Docker'],
            'experience': [
                {
                    'title': 'Senior ML Engineer',
                    'company': 'Tech Corp',
                    'duration_months': 36,
                    'description': 'Led ML team of 5 engineers. Increased model accuracy by 40%. Delivered 3 major ML projects, processing 1M records/day. Reduced costs by $200K through optimization.'
                },
                {
                    'title': 'ML Engineer',
                    'company': 'AI Startup',
                    'duration_months': 24,
                    'description': 'Built production ML pipelines. Improved deployment speed by 60%. Achieved 95% accuracy on classification tasks.'
                }
            ],
            'education': [
                {'degree': 'Master of Science', 'field': 'Computer Science', 'institution': 'MIT'}
            ],
            'experience_years': 5,
            'sections': {
                'summary': {'content': 'Senior ML engineer with 5 years experience in production ML systems'},
                'experience': {'content': 'Led ML team of 5 engineers. Increased model accuracy by 40%. Built production ML pipelines. Delivered 3 major projects.'},
                'skills': {'content': 'Python, Machine Learning, TensorFlow, PyTorch, AWS, Docker, Kubernetes'},
                'education': {'content': 'MS Computer Science, MIT, 2018. BS Computer Science, Stanford, 2016'},
                'projects': {'content': 'Built ML pipeline processing 1M records/day. Achieved 95% accuracy on classification task.'}
            },
            'full_text': '''Alice Johnson
Senior ML Engineer | alice@email.com | 555-1234 | linkedin.com/in/alice

EXPERIENCE
Senior ML Engineer at Tech Corp (3 years)
• Led ML team of 5 engineers, increased model accuracy by 40%
• Delivered 3 major ML projects ahead of schedule
• Reduced costs by $200K through AWS optimization
• Improved deployment speed by 60%

ML Engineer at AI Startup (2 years)
• Built production ML pipelines processing 1M records/day
• Achieved 95% accuracy on classification tasks

SKILLS
Python, Machine Learning, TensorFlow, PyTorch, AWS, Docker, Kubernetes

EDUCATION
MS Computer Science, MIT, 2018
BS Computer Science, Stanford, 2016''',
            'metadata': {'email': 'alice@email.com', 'phone': '555-1234', 'linkedin': 'linkedin.com/in/alice'}
        },
        {
            'resume_id': 'average_candidate.pdf',
            'name': 'Bob Smith',
            'email': 'bob@email.com',
            'skills': ['Python', 'SQL', 'Excel'],
            'experience': [
                {
                    'title': 'Data Analyst',
                    'company': 'Small Corp',
                    'duration_months': 18,
                    'description': 'Analyzed data and created reports'
                }
            ],
            'education': [
                {'degree': 'Bachelor of Science', 'field': 'Statistics'}
            ],
            'experience_years': 1.5,
            'sections': {
                'experience': {'content': 'Data Analyst at Small Corp. Analyzed data and created reports.'},
                'skills': {'content': 'Python, SQL, Excel'},
                'education': {'content': 'BS Statistics'}
            },
            'full_text': '''Bob Smith
bob@email.com

Data Analyst at Small Corp (1.5 years)
Analyzed data and created reports

Skills: Python, SQL, Excel
Education: BS Statistics''',
            'metadata': {'email': 'bob@email.com'}
        },
        {
            'resume_id': 'poor_candidate.pdf',
            'name': 'Charlie Brown',
            'skills': ['Computers'],
            'experience': [
                {
                    'title': 'Intern',
                    'duration_months': 6,
                    'description': 'I did some work'
                }
            ],
            'experience_years': 0.5,
            'sections': {
                'experience': {'content': 'I did some work at a company'}
            },
            'full_text': '''My name is Charlie Brown
I am looking for a job

I did some work at a company as an intern
References available upon request''',
            'metadata': {}
        }
    ]
    
    # Index resumes
    print("\n📊 Indexing resumes...")
    for resume in resumes:
        engine.index_resume(resume)
    print(f"✅ Indexed {len(resumes)} resumes\n")
    
    # Create job description
    job = {
        'title': 'Senior Machine Learning Engineer',
        'description': 'Looking for experienced ML engineer with Python and TensorFlow',
        'required_skills': ['Python', 'Machine Learning', 'TensorFlow'],
        'optional_skills': ['AWS', 'Docker', 'Kubernetes'],
        'experience_years': 3,
        'experience_level': 'senior',
        'required_degree': 'Bachelor',
        'required_field': 'Computer Science'
    }
    
    print("=" * 90)
    print("📋 JOB POSTING")
    print("=" * 90)
    print(f"Title: {job['title']}")
    print(f"Required Skills: {', '.join(job['required_skills'])}")
    print(f"Optional Skills: {', '.join(job['optional_skills'])}")
    print(f"Experience: {job['experience_years']}+ years ({job['experience_level']} level)")
    
    # Find matches
    print("\n" + "=" * 90)
    print("🔍 FINDING MATCHES...")
    print("=" * 90)
    
    matches = engine.find_matches(job, top_k=10)
    
    print("\n" + "=" * 90)
    print("📊 RESULTS - RANKED CANDIDATES")
    print("=" * 90)
    
    for i, match in enumerate(matches, 1):
        print(f"\n{'━' * 90}")
        print(f"#{i} {match['name']}")
        print(f"{'━' * 90}")
        
        # Match score
        match_score = match['match_score']
        match_tier = match.get('tier', 'Unknown')
        print(f"   🎯 Match Score: {match_score:.1f}/100 ({match_tier})")
        
        # Quality score
        quality_score = match.get('quality_score', 0)
        quality_grade = match.get('quality_grade', 'N/A')
        print(f"   ⭐ Quality Score: {quality_score:.1f}/10 ({quality_grade})")
        
        # Combined assessment
        combined = (match_score + quality_score * 10) / 2
        print(f"   📈 Combined Score: {combined:.1f}/100")
        
        # Details
        print(f"\n   📧 {match.get('email', 'No email')}")
        print(f"   💼 {match.get('experience_years', 0)} years experience")
        print(f"   🛠️  Skills: {', '.join(match.get('skills', [])[:5])}")
        
        # Match breakdown
        details = match.get('match_details', {})
        if details:
            scores = details.get('scores', {})
            print(f"\n   Match Breakdown:")
            print(f"     • Semantic: {scores.get('semantic', 0):.0f}/100")
            print(f"     • Skills: {scores.get('skills', 0):.0f}/100")
            print(f"     • Experience: {scores.get('experience', 0):.0f}/100")
            print(f"     • Education: {scores.get('education', 0):.0f}/100")
        
        # Quality breakdown
        quality_details = match.get('quality_details', {})
        if quality_details:
            factors = quality_details.get('factors', {})
            print(f"\n   Quality Breakdown:")
            print(f"     • Formatting: {factors.get('formatting', 0):.1f}/10")
            print(f"     • Completeness: {factors.get('completeness', 0):.1f}/10")
            print(f"     • Clarity: {factors.get('clarity', 0):.1f}/10")
            print(f"     • Quantification: {factors.get('quantification', 0):.1f}/10")
        
        # Recommendations
        strengths = details.get('strengths', [])
        if strengths:
            print(f"\n   ✅ Strengths:")
            for strength in strengths[:3]:
                print(f"      • {strength}")
        
        recommendations = quality_details.get('recommendations', [])
        if recommendations:
            print(f"\n   💡 Resume Improvements:")
            for rec in recommendations[:2]:
                print(f"      • {rec}")
    
    print("\n" + "=" * 90)
    print("✅ TEST COMPLETE")
    print("=" * 90)
    print("\nKey Insights:")
    print("  • Match Score: How well they fit the job requirements")
    print("  • Quality Score: How professional and well-written their resume is")
    print("  • Combined Score: Overall candidate assessment")


if __name__ == "__main__":
    test_complete_pipeline()
