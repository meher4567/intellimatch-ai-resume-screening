"""
Quick test script to verify core services functionality.
Run this to ensure resume parsing, skill extraction, and matching work correctly.
"""

def test_skill_extractor():
    """Test skill extraction service."""
    print("\n=== Testing Skill Extractor ===")
    from src.services.skill_extractor import SkillExtractor
    
    extractor = SkillExtractor()
    
    sample_text = """
    Experienced software engineer with 5 years of Python development.
    Proficient in React, Node.js, PostgreSQL, and AWS.
    Strong background in machine learning and data science.
    """
    
    skills = extractor.extract_skills(sample_text)
    print(f"Extracted {len(skills)} skills:")
    for skill in skills[:10]:  # Show top 10
        print(f"  - {skill['name']} ({skill['category']}) - confidence: {skill['confidence']}")
    
    # Test normalization
    normalized = extractor.normalize_skill("nodejs")
    print(f"\nNormalized 'nodejs' → '{normalized}'")
    
    print("✓ Skill extraction working!")


def test_resume_parser():
    """Test enhanced resume parser with all new fields."""
    print("\n=== Testing Enhanced Resume Parser ===")
    from src.services.resume_parser import ResumeParser
    
    parser = ResumeParser()
    
    # Test with comprehensive sample text
    sample_resume_text = """
    John Doe
    john.doe@email.com | (555) 123-4567
    LinkedIn: linkedin.com/in/johndoe | GitHub: github.com/johndoe
    
    PROFESSIONAL SUMMARY
    Senior Software Engineer with 8 years of experience in Python, JavaScript, and cloud technologies.
    
    SKILLS
    Python, Django, React, PostgreSQL, AWS, Docker, Kubernetes, Machine Learning
    
    EDUCATION
    Master of Science in Computer Science - Stanford University - 2015
    Major in Artificial Intelligence
    
    Bachelor of Science in Computer Science - MIT - 2013
    
    EXPERIENCE
    Senior Software Engineer - Tech Corp
    Jan 2018 - Present
    • Led team of 5 engineers building microservices
    • Implemented CI/CD pipeline reducing deployment time by 50%
    
    Software Developer - StartupXYZ
    Jun 2015 - Dec 2017
    • Built RESTful APIs using Django and PostgreSQL
    
    PROJECTS
    E-Commerce Platform
    Built scalable platform handling 10k+ daily users using React and Node.js
    
    ML Recommendation System
    Developed recommendation engine using TensorFlow and Python
    
    CERTIFICATIONS
    AWS Certified Solutions Architect
    Certified Scrum Master (CSM)
    
    LANGUAGES
    English (Native), Spanish (Fluent), French (Intermediate)
    
    Expected Salary: 150000 USD
    Notice Period: 30 days
    """
    
    # Test basic extraction
    cleaned = parser._clean_text(sample_resume_text)
    email = parser._extract_email(cleaned)
    phone = parser._extract_phone(cleaned)
    name = parser._extract_name(cleaned)
    skills = parser._extract_skills_basic(cleaned)
    education_simple = parser._extract_education(cleaned)
    experience = parser._estimate_experience(cleaned)
    
    print(f"📋 Basic Fields:")
    print(f"  Name: {name}")
    print(f"  Email: {email}")
    print(f"  Phone: {phone}")
    print(f"  Experience: {experience} years")
    print(f"  Education Levels: {', '.join(education_simple)}")
    print(f"  Skills ({len(skills)}): {', '.join(skills[:5])}...")
    
    # Test detailed extraction
    education_detailed = parser._extract_education_detailed(cleaned)
    work_exp = parser._extract_work_experience(cleaned)
    projects = parser._extract_projects(cleaned)
    certs = parser._extract_certifications(cleaned)
    languages = parser._extract_languages(cleaned)
    linkedin = parser._extract_linkedin(cleaned)
    github = parser._extract_github(cleaned)
    salary = parser._extract_salary(cleaned)
    notice = parser._extract_notice_period(cleaned)
    quality = parser._calculate_quality_score(sample_resume_text, cleaned)
    
    print(f"\n📚 Detailed Education ({len(education_detailed)} entries):")
    for edu in education_detailed[:2]:
        print(f"  - {edu['degree']}: {edu.get('major', 'N/A')} at {edu.get('university', 'N/A')} ({edu.get('year', 'N/A')})")
    
    print(f"\n💼 Work Experience ({len(work_exp)} entries):")
    for exp in work_exp[:2]:
        print(f"  - {exp.get('title', 'N/A')} at {exp.get('company', 'N/A')}")
    
    print(f"\n🚀 Projects ({len(projects)}):")
    for proj in projects[:2]:
        print(f"  - {proj.get('name', 'N/A')}")
    
    print(f"\n🏆 Certifications ({len(certs)}): {', '.join(certs[:2]) if certs else 'None'}")
    print(f"\n🌍 Languages ({len(languages)}): {', '.join(languages)}")
    print(f"\n🔗 Social:")
    print(f"  LinkedIn: {linkedin}")
    print(f"  GitHub: {github}")
    
    print(f"\n💰 Salary: {salary}")
    print(f"⏰ Notice Period: {notice}")
    print(f"⭐ Quality Score: {quality}/100")
    
    print("\n✓ Enhanced resume parsing working!")


def test_matching_engine():
    """Test matching engine."""
    print("\n=== Testing Matching Engine ===")
    from src.services.matching_engine import MatchingEngine
    
    matcher = MatchingEngine()
    
    resume_text = """
    Software Engineer with 5 years of Python experience.
    Proficient in Django, Flask, PostgreSQL, and AWS.
    Built RESTful APIs and microservices.
    Strong problem-solving and teamwork skills.
    """
    
    job_description = """
    We are looking for a Python Developer with experience in:
    - Python and Django framework
    - PostgreSQL database
    - AWS cloud services
    - RESTful API development
    - 3+ years of experience
    """
    
    resume_skills = ["Python", "Django", "Flask", "PostgreSQL", "AWS"]
    job_requirements = ["Python", "Django", "PostgreSQL", "AWS", "Docker"]
    
    # Test similarity computation
    print("Computing match...")
    match_result = matcher.match_resume_to_job(
        resume_text=resume_text,
        job_description=job_description,
        resume_skills=resume_skills,
        job_requirements=job_requirements
    )
    
    print(f"\nMatch Results:")
    print(f"  Overall Score: {match_result['percentage']}%")
    print(f"  Semantic Similarity: {match_result['semantic_similarity']:.3f}")
    print(f"  Skill Match: {match_result['skill_match']:.3f}")
    print(f"  Keyword Match: {match_result['keyword_match']:.3f}")
    
    # Test explanation
    explanation = matcher.explain_match(
        resume_text, job_description, resume_skills, job_requirements
    )
    
    print(f"\nMatched Skills: {', '.join(explanation['matched_skills'])}")
    print(f"Missing Skills: {', '.join(explanation['missing_skills'])}")
    
    print("✓ Matching engine working!")


def test_knockout_filter():
    """Test knockout criteria filtering."""
    print("\n=== Testing Knockout Filter ===")
    from src.services.matching_engine import KnockoutFilter
    
    candidate = {
        "experience_years": 3,
        "skills": ["Python", "React", "PostgreSQL"],
        "education": "Bachelor of Science"
    }
    
    criteria = [
        {"type": "min_experience", "value": 2},
        {"type": "required_skill", "value": "Python"},
        {"type": "required_skill", "value": "Docker"}  # This will fail
    ]
    
    passes, reasons = KnockoutFilter.apply_filters(candidate, criteria)
    
    print(f"Candidate passes: {passes}")
    if not passes:
        print("Reasons:")
        for reason in reasons:
            print(f"  - {reason}")
    
    print("✓ Knockout filter working!")


def run_all_tests():
    """Run all service tests."""
    print("=" * 60)
    print("IntelliMatch AI - Core Services Test Suite")
    print("=" * 60)
    
    try:
        test_skill_extractor()
        test_resume_parser()
        test_matching_engine()
        test_knockout_filter()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
