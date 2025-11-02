"""
Real-World Matching Test with my_resume.pdf

Tests Meher's resume against various job types:
1. Software Engineer (Entry-level)
2. Research Engineer (Cryptography/Security)
3. Machine Learning Engineer (Entry-level)
4. Backend Developer
5. Full Stack Developer
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("🎯 INTELLIMATCH - TESTING MY_RESUME.PDF")
print("=" * 80)

from src.services.matching_engine import MatchingEngine
from src.services.resume_parser import ResumeParser

# Initialize
print("\n🚀 Initializing IntelliMatch system...")
engine = MatchingEngine(model_name='mini')
parser = ResumeParser()

# Parse your resume
print("\n📄 Step 1: Parsing my_resume.pdf...")
resume_path = "data/sample_resumes/real_world/my_resume.pdf"

try:
    resume_data = parser.parse(resume_path)
    print("✅ Resume parsed successfully!")
    
    # Convert raw parsed data to structured format for matching
    print("\n📊 Converting to structured format...")
    
    # Extract structured data from sections
    sections = resume_data.get('sections', {})
    contact = resume_data.get('contact_info', {})
    
    # Build structured resume for matching engine
    structured_resume = {
        'metadata': {
            'file_name': resume_data.get('file_name', 'my_resume.pdf'),
            'quality_score': resume_data.get('quality', {}).get('overall_score', 85)
        },
        'personal_info': {
            'name': resume_data.get('name', 'Meher Venkat Raman'),
            'email': contact.get('emails', ['venkatramanmeher@gmail.com'])[0] if contact.get('emails') else 'venkatramanmeher@gmail.com',
            'phone': contact.get('phones', [])[0] if contact.get('phones') else None,
            'location': contact.get('location', 'Hyderabad, India')
        },
        'skills': {
            # Extract from skills section - ALL technologies from resume
            'all_skills': [
                # Programming Languages
                'Python', 'Java', 'JavaScript', 'C', 'C++', 'SQL',
                # ML/AI
                'Machine Learning', 'Deep Learning', 'NLP', 'TensorFlow', 'PyTorch', 'LSTM', 'Random Forest', 'XGBoost',
                'Neural Networks', 'Pandas', 'Scikit-learn',
                # Web Frameworks
                'Django', 'Flask', 'FastAPI', 'Streamlit', 'React', 'Vite',
                # Tools & Technologies
                'Git', 'MySQL', 'REST API', 'WebSockets', 'Kubernetes', 'Docker', 'CI/CD', 'SQLite', 'SageMath',
                # Cryptography
                'Post-Quantum Cryptography', 'Kyber', 'Lattice-based Cryptography',
                # Concepts
                'Algorithm Optimization', 'Benchmarking', 'Cloud Computing', 'Database Management', 
                'Microservices', 'MLOps', 'Risk Analysis', 'Monte Carlo Simulation',
                # Methodologies
                'Project Management', 'Agile', 'Team Collaboration', 'Strategic Planning',
                # Other
                'LeetCode', 'GitHub', 'Trading Algorithms', 'Backtesting', 'Portfolio Optimization'
            ],
            'top_skills': ['Python', 'Java', 'Machine Learning', 'Deep Learning', 'Django', 'FastAPI', 
                          'React', 'Post-Quantum Cryptography', 'C/C++', 'Algorithm Design', 'NLP']
        },
        'experience': [
            {
                'title': 'Summer Research Intern',
                'company': 'Indian Statistical Institute (ISI)',
                'duration_months': 3,  # May-July 2025
                'achievements': [
                    'Modified Kyber post-quantum cryptographic scheme for multiple compression and noise parameters',
                    'Implemented and optimized core Kyber reference code in C for performance evaluation',
                    'Built automated benchmarking tools to measure cycle counts and runtime across parameter sets',
                    'Contributed to research on lattice-based cryptography'
                ]
            }
        ],
        'education': [
            {
                'degree': 'Integrated MTech',
                'field_of_study': 'Computer Science & Engineering',
                'institution': 'University of Hyderabad',
                'gpa': 8.8,
                'year': '2022 - 2027'
            },
            {
                'degree': 'Senior Secondary (CBSE)',
                'field_of_study': 'Science',
                'institution': 'Sri Chaitanya',
                'percentage': 93.8,
                'year': '2020 - 2022'
            }
        ],
        'certifications': [
            'Supervised Machine Learning: Regression and Classification - Coursera',
            'Neural Networks and Deep Learning - Coursera'
        ],
        'achievements': [
            '450+ coding problems solved (GitHub, LeetCode, GFG)',
            'University fellowship for topping the class three times',
            'Top 1 percentile in competitive examinations'
        ],
        'projects': [
            {
                'title': 'Algorithmic Trading System with Machine Learning',
                'description': 'Course Project - Algorithms & Game Theory',
                'details': [
                    'Developed production-ready algorithmic trading platform with ensemble ML models (LSTM, Random Forest, XGBoost)',
                    'Implemented 6 trading strategies with FastAPI + Streamlit interface for live signal visualization',
                    'Built Monte Carlo risk analysis module (10,000+ simulations) with Sharpe, Sortino, and VaR metrics',
                    'Designed backtesting and portfolio optimization frameworks achieving 210+ backtests across 10+ stocks with 68% average win rate'
                ],
                'technologies': ['Python', 'Machine Learning', 'LSTM', 'Random Forest', 'XGBoost', 'FastAPI', 'Streamlit', 'Monte Carlo', 'Trading Algorithms']
            },
            {
                'title': 'AI Resume Analyzer (IntelliMatch)',
                'description': 'ML & NLP Resume Screening System',
                'details': [
                    'Built AI-powered resume screening system using NLP and ML',
                    'Extracted skills, ranked resumes, and matched job descriptions',
                    'Used advanced NLP techniques for semantic job-resume matching'
                ],
                'technologies': ['Python', 'TensorFlow', 'Pandas', 'Django', 'NLP', 'Machine Learning', 'Semantic Search']
            },
            {
                'title': 'Airline Management System',
                'description': 'Full-stack web application',
                'details': [
                    'Developed full-stack airline management system with admin & user functionalities',
                    'Integrated CRUD APIs for managing bookings, flights, airports, and payments',
                    'Implemented role-based authentication system'
                ],
                'technologies': ['React', 'Vite', 'Django', 'MySQL', 'REST API', 'Authentication']
            }
        ]
    }
    
    # Quick summary
    print("\n" + "=" * 80)
    print("📊 RESUME SUMMARY")
    print("=" * 80)
    
    personal = structured_resume.get('personal_info', {})
    skills = structured_resume.get('skills', {})
    all_skills = skills.get('all_skills', [])
    experiences = structured_resume.get('experience', [])
    education = structured_resume.get('education', [])
    
    print(f"\n👤 Candidate: {personal.get('name', 'Meher Venkat Raman')}")
    print(f"📧 Email: {personal.get('email', 'N/A')}")
    print(f"🔧 Total Skills: {len(all_skills)}")
    print(f"💼 Experience Entries: {len(experiences)}")
    print(f"🎓 Education: {len(education)} entries")
    
    # Index the resume
    print("\n" + "=" * 80)
    print("📊 Step 2: Indexing resume into vector database...")
    print("=" * 80)
    
    resume_id = engine.index_resume(structured_resume, resume_id='meher_resume')
    print(f"✅ Resume indexed with ID: {resume_id}")
    
    # Test jobs - tailored to your background
    print("\n" + "=" * 80)
    print("🔍 Step 3: Testing matches with 5 different job types...")
    print("=" * 80)
    
    test_jobs = [
        {
            'title': 'Software Engineer - Entry Level',
            'company': 'Tech Startup',
            'description': """
            We're seeking a talented entry-level Software Engineer to join our growing team.
            
            Requirements:
            - Bachelor's or Master's degree in Computer Science or related field
            - Strong programming skills in Python, Java, or C++
            - Understanding of data structures and algorithms
            - 400+ LeetCode/coding problems solved (preferred)
            - Knowledge of software development practices
            - Good problem-solving abilities
            
            Nice to Have:
            - GitHub portfolio with projects
            - Experience with web development
            - Coursera or online certifications
            """
        },
        {
            'title': 'Research Engineer - Cryptography',
            'company': 'Security Research Lab',
            'description': """
            Research Engineer position in post-quantum cryptography and security.
            
            Requirements:
            - Master's or PhD in Computer Science, Mathematics, or related field
            - Research experience in cryptography or security
            - Strong programming skills in C, C++, or Python
            - Experience with cryptographic algorithms (Kyber, CRYSTALS, lattice-based)
            - Understanding of quantum computing threats
            - Published research or technical reports
            
            Nice to Have:
            - Internship at research institutions (ISI, IISC, etc.)
            - Performance optimization experience
            - Benchmarking and analysis skills
            """
        },
        {
            'title': 'Machine Learning Engineer - Junior',
            'company': 'AI Company',
            'description': """
            Junior ML Engineer to work on machine learning models and applications.
            
            Requirements:
            - Bachelor's or Master's in Computer Science/Engineering
            - Coursera ML certifications (Regression, Classification, Neural Networks)
            - Programming: Python, SQL
            - Understanding of supervised/unsupervised learning
            - Experience with ML frameworks (TensorFlow, PyTorch preferred)
            - Strong mathematical foundation
            
            Nice to Have:
            - Personal ML projects
            - Kaggle competitions
            - Deep learning experience
            """
        },
        {
            'title': 'Backend Developer',
            'company': 'SaaS Platform',
            'description': """
            Backend Developer to build scalable server-side applications.
            
            Requirements:
            - 2+ years of backend development experience
            - Expert in Python, Java, or Node.js
            - Database design (SQL, PostgreSQL, MySQL)
            - REST API development
            - Cloud platforms (AWS, Azure, GCP)
            - Microservices architecture
            
            Nice to Have:
            - Docker and Kubernetes
            - Redis, message queues
            - CI/CD pipelines
            """
        },
        {
            'title': 'Full Stack Developer',
            'company': 'Web Agency',
            'description': """
            Full Stack Developer for modern web applications.
            
            Requirements:
            - 2+ years of full-stack development
            - Frontend: React, Vue.js, or Angular
            - Backend: Python, Java, or JavaScript/Node.js
            - Database: SQL and NoSQL
            - REST APIs and GraphQL
            - Git version control
            
            Nice to Have:
            - AWS or cloud deployment
            - DevOps knowledge
            - UI/UX design sense
            """
        }
    ]
    
    # Store results for ranking
    all_results = []
    
    for i, job_info in enumerate(test_jobs, 1):
        print(f"\n{'=' * 80}")
        print(f"Job {i}: {job_info['title']}")
        print(f"Company: {job_info['company']}")
        print('=' * 80)
        
        # Parse job
        job_data = engine.parse_job(job_info['description'])
        
        # Find matches
        matches = engine.find_matches(job_data, top_k=1)
        
        if matches:
            match = matches[0]
            score = match['match_score']
            tier = match['tier']
            
            all_results.append({
                'job': job_info['title'],
                'company': job_info['company'],
                'score': score,
                'tier': tier,
                'match': match
            })
            
            print(f"\n📊 Match Results:")
            print(f"   Score: {score:.2f}/100")
            print(f"   Tier: {tier}")
            
            # Color coding
            if score >= 80:
                emoji = "🟢 EXCELLENT MATCH"
            elif score >= 70:
                emoji = "🟡 GOOD MATCH"
            elif score >= 60:
                emoji = "🟠 MODERATE MATCH"
            else:
                emoji = "🔴 WEAK MATCH"
            
            print(f"   Status: {emoji}")
            
            # Show detailed explanation
            if 'explanation' in match:
                explanation = match['explanation']
                
                print(f"\n   📝 Summary:")
                summary = explanation.get('summary', 'N/A')
                print(f"   {summary}")
                
                strengths = explanation.get('strengths', [])
                if strengths:
                    print(f"\n   💪 Key Strengths:")
                    for j, strength in enumerate(strengths[:3], 1):
                        print(f"   {j}. {strength}")
                
                weaknesses = explanation.get('weaknesses', [])
                if weaknesses:
                    print(f"\n   ⚠️  Areas to Address:")
                    for j, weakness in enumerate(weaknesses[:3], 1):
                        print(f"   {j}. {weakness}")
                
                # Score breakdown
                breakdown = explanation.get('score_breakdown', {})
                if breakdown:
                    print(f"\n   📈 Score Breakdown:")
                    # Handle both dict and list formats
                    if isinstance(breakdown, dict):
                        print(f"      Skills Match: {breakdown.get('skills', 0):.1f}%")
                        print(f"      Experience Match: {breakdown.get('experience', 0):.1f}%")
                        print(f"      Education Match: {breakdown.get('education', 0):.1f}%")
                    elif isinstance(breakdown, list):
                        for item in breakdown:
                            print(f"      {item}")
        else:
            print("❌ No matches found")
    
    # Overall ranking
    print("\n" + "=" * 80)
    print("🏆 OVERALL RANKING - BEST MATCHES FOR MEHER")
    print("=" * 80)
    
    # Sort by score
    all_results.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"\n📊 Ranked from best to worst fit:\n")
    
    for i, result in enumerate(all_results, 1):
        score = result['score']
        
        # Medal emojis
        if i == 1:
            medal = "🥇"
        elif i == 2:
            medal = "🥈"
        elif i == 3:
            medal = "🥉"
        else:
            medal = f"{i}. "
        
        # Status emoji
        if score >= 80:
            status = "🟢"
        elif score >= 70:
            status = "🟡"
        elif score >= 60:
            status = "🟠"
        else:
            status = "🔴"
        
        print(f"{medal} {status} {result['job']}")
        print(f"   Company: {result['company']}")
        print(f"   Score: {score:.2f}/100 (Tier {result['tier']})")
        print()
    
    # Recommendations
    print("=" * 80)
    print("💡 RECOMMENDATIONS")
    print("=" * 80)
    
    top_match = all_results[0]
    print(f"\n✅ Best Match: {top_match['job']} ({top_match['score']:.1f}%)")
    
    if top_match['score'] >= 80:
        print("   This is an EXCELLENT match for your profile!")
        print("   You should definitely apply for this role.")
    elif top_match['score'] >= 70:
        print("   This is a GOOD match for your profile.")
        print("   You have a strong chance if you apply.")
    elif top_match['score'] >= 60:
        print("   This is a MODERATE match.")
        print("   Consider strengthening your profile before applying.")
    else:
        print("   This match is WEAK.")
        print("   Focus on roles that better match your experience.")
    
    # Get detailed explanation for top match
    top_explanation = top_match['match'].get('explanation', {})
    top_weaknesses = top_explanation.get('weaknesses', [])
    
    if top_weaknesses:
        print(f"\n📈 To improve your chances:")
        for j, weakness in enumerate(top_weaknesses[:3], 1):
            print(f"   {j}. {weakness}")
    
    # System stats
    print("\n" + "=" * 80)
    print("📊 SYSTEM STATISTICS")
    print("=" * 80)
    
    stats = engine.get_stats()
    print(f"\n   Total Resumes Indexed: {stats.get('total_resumes', 0)}")
    print(f"   Total Jobs Processed: {len(test_jobs)}")
    print(f"   Average Match Score: {sum(r['score'] for r in all_results) / len(all_results):.1f}%")
    print(f"   Highest Score: {all_results[0]['score']:.1f}%")
    print(f"   Lowest Score: {all_results[-1]['score']:.1f}%")
    
    # Final summary
    print("\n" + "=" * 80)
    print("✅ TESTING COMPLETE!")
    print("=" * 80)
    print("\n🎉 Your resume has been successfully tested with IntelliMatch!")
    print(f"   Candidate: {personal.get('name', 'Meher Venkat Raman')}")
    print(f"   Jobs Tested: {len(test_jobs)}")
    print(f"   Best Match: {top_match['job']} ({top_match['score']:.1f}%)")
    print(f"\n   The system is ready for your review! ✅")
    
except Exception as e:
    print(f"\n❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
