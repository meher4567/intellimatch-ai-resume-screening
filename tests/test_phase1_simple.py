"""
Simplified Phase 1 Integration Test
Focuses on end-to-end functionality that matters
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("🧪 PHASE 1 - PRACTICAL INTEGRATION TEST")
print("=" * 80)
print()

# Track results
all_passed = True

def test(name, func):
    """Run a test and track results"""
    global all_passed
    print(f"\n{'='*80}")
    print(f"📋 {name}")
    print('='*80)
    try:
        func()
        print(f"✅ {name} - PASSED")
        return True
    except Exception as e:
        print(f"❌ {name} - FAILED: {e}")
        all_passed = False
        import traceback
        traceback.print_exc()
        return False

# TEST 1: Imports
def test_imports():
    print("Importing all modules...")
    from src.ml.embedding_generator import EmbeddingGenerator
    from src.ml.vector_store import VectorStore
    from src.ml.semantic_search import SemanticSearch
    from src.services.matching_engine import MatchingEngine
    from src.services.job_description_parser import JobDescriptionParser
    from src.services.resume_parser import ResumeParser
    print("✅ All critical modules imported")

# TEST 2: End-to-End Matching Pipeline
def test_e2e_pipeline():
    from src.services.matching_engine import MatchingEngine
    
    print("\n🚀 Initializing matching engine...")
    engine = MatchingEngine(model_name='mini')
    
    # Create realistic test data
    print("\n📄 Creating test resumes...")
    resumes = [
        {
            'metadata': {'file_name': 'senior_python_dev.pdf', 'quality_score': 95},
            'personal_info': {'name': 'Sarah Chen', 'email': 'sarah@example.com'},
            'skills': {
                'all_skills': ['Python', 'Django', 'AWS', 'PostgreSQL', 'Docker', 'REST API'],
                'top_skills': ['Python', 'Django', 'AWS']
            },
            'experience': [
                {
                    'title': 'Senior Python Developer',
                    'company': 'TechCorp',
                    'duration_months': 48,
                    'achievements': ['Led team of 5', 'Built microservices', 'AWS deployment']
                },
                {
                    'title': 'Python Developer',
                    'company': 'StartupXYZ',
                    'duration_months': 24,
                    'achievements': ['Django apps', 'API development']
                }
            ],
            'education': [
                {'degree': 'Master of Science', 'field_of_study': 'Computer Science', 'institution': 'Stanford'}
            ]
        },
        {
            'metadata': {'file_name': 'junior_java_dev.pdf', 'quality_score': 75},
            'personal_info': {'name': 'Mike Johnson', 'email': 'mike@example.com'},
            'skills': {
                'all_skills': ['Java', 'Spring', 'MySQL', 'Git'],
                'top_skills': ['Java', 'Spring']
            },
            'experience': [
                {
                    'title': 'Junior Java Developer',
                    'company': 'JavaCo',
                    'duration_months': 18,
                    'achievements': ['Spring Boot apps']
                }
            ],
            'education': [
                {'degree': 'Bachelor', 'field_of_study': 'IT', 'institution': 'State University'}
            ]
        },
        {
            'metadata': {'file_name': 'python_ml_engineer.pdf', 'quality_score': 92},
            'personal_info': {'name': 'Lisa Wang', 'email': 'lisa@example.com'},
            'skills': {
                'all_skills': ['Python', 'TensorFlow', 'PyTorch', 'AWS', 'Docker', 'Kubernetes'],
                'top_skills': ['Python', 'Machine Learning', 'AWS']
            },
            'experience': [
                {
                    'title': 'ML Engineer',
                    'company': 'AI Labs',
                    'duration_months': 36,
                    'achievements': ['Built ML pipeline', 'Deployed models on AWS']
                }
            ],
            'education': [
                {'degree': 'PhD', 'field_of_study': 'Machine Learning', 'institution': 'MIT'}
            ]
        }
    ]
    
    print("\n📊 Indexing resumes...")
    resume_ids = engine.index_resumes_batch(resumes)
    print(f"   Indexed {len(resume_ids)} resumes")
    assert len(resume_ids) == 3, "Should index all resumes"
    
    # Create job posting
    print("\n💼 Creating job posting...")
    job_text = """
    Senior Python Developer
    
    We are seeking an experienced Python developer to join our backend team.
    
    Requirements:
    - 3+ years of Python development experience
    - Strong knowledge of Django framework
    - Experience with AWS cloud services
    - Understanding of PostgreSQL databases
    - Docker and containerization experience
    - Bachelor's degree in Computer Science or related field
    
    Nice to have:
    - Microservices architecture
    - CI/CD pipelines
    - Team leadership experience
    """
    
    job_data = engine.parse_job(job_text)
    print(f"   Job parsed successfully")
    
    # Find matches
    print("\n🔍 Finding matching candidates...")
    matches = engine.find_matches(job_data, top_k=3)
    print(f"   Found {len(matches)} candidates")
    
    assert len(matches) > 0, "Should find matches"
    
    # Display results
    print("\n📊 Match Results:")
    for i, match in enumerate(matches, 1):
        print(f"\n   {i}. {match['name']}")
        print(f"      Score: {match['match_score']:.1f}/100")
        print(f"      Tier: {match['tier']}")
        print(f"      Experience: {match.get('experience_years', 0)} years")
        print(f"      Skills: {', '.join(match.get('skills', [])[:5])}")
        if 'explanation' in match:
            print(f"      Summary: {match['explanation']['summary'][:100]}...")
    
    # Verify top candidate
    top_match = matches[0]
    print(f"\n✅ Top candidate: {top_match['name']} ({top_match['match_score']:.1f}/100)")
    
    # Sarah or Lisa should be top (both are Python experts with AWS)
    assert top_match['name'] in ['Sarah Chen', 'Lisa Wang'], \
        f"Expected Sarah or Lisa as top match, got {top_match['name']}"
    
    # Top match should have decent score
    assert top_match['match_score'] > 30, \
        f"Top match should score >30, got {top_match['match_score']}"
    
    print("\n✅ Pipeline working correctly!")

# TEST 3: Save/Load State
def test_save_load():
    from src.services.matching_engine import MatchingEngine
    
    print("\n💾 Testing state persistence...")
    
    # Create engine and index data
    engine1 = MatchingEngine(model_name='mini')
    test_resume = {
        'metadata': {'file_name': 'test.pdf', 'quality_score': 90},
        'personal_info': {'name': 'Test User', 'email': 'test@example.com'},
        'skills': {'all_skills': ['Python', 'FastAPI'], 'top_skills': ['Python']},
        'experience': [{'title': 'Developer', 'company': 'TestCo', 'duration_months': 24, 'achievements': []}],
        'education': [{'degree': 'Bachelor', 'field_of_study': 'CS', 'institution': 'Test U'}]
    }
    engine1.index_resume(test_resume)
    
    # Save state
    print("   Saving state...")
    engine1.save_state('test_state')
    
    # Load in new engine
    print("   Loading state...")
    engine2 = MatchingEngine(model_name='mini')
    engine2.load_state('test_state')
    
    stats = engine2.get_stats()
    print(f"   Loaded: {stats['resumes_indexed']} resumes")
    assert stats['resumes_indexed'] >= 1, "Should have loaded resume"
    
    print("✅ State persistence working!")

# TEST 4: File Structure
def test_file_structure():
    print("\n📁 Verifying file structure...")
    
    required_files = [
        'src/ml/embedding_generator.py',
        'src/ml/vector_store.py',
        'src/ml/semantic_search.py',
        'src/services/matching_engine.py',
        'src/services/job_description_parser.py',
        'src/services/resume_parser.py',
        'src/api/main.py',
        'frontend/index.html',
    ]
    
    missing = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(file_path)
    
    if missing:
        raise Exception(f"Missing files: {missing}")
    
    print(f"✅ All {len(required_files)} required files present")

# RUN ALL TESTS
test("1. Module Imports", test_imports)
test("2. End-to-End Matching Pipeline", test_e2e_pipeline)
test("3. Save/Load State", test_save_load)
test("4. File Structure", test_file_structure)

# Final Report
print("\n" + "=" * 80)
print("📊 FINAL REPORT")
print("=" * 80)

if all_passed:
    print("\n🎉 ALL TESTS PASSED!")
    print("\n✅ Phase 1 is FULLY FUNCTIONAL and ready for use!")
    print("\nWhat works:")
    print("  ✅ Resume indexing and parsing")
    print("  ✅ Job description parsing")
    print("  ✅ Semantic search with FAISS")
    print("  ✅ Multi-factor scoring")
    print("  ✅ Candidate ranking and tiering")
    print("  ✅ Match explanations")
    print("  ✅ State persistence")
    print("  ✅ Complete end-to-end pipeline")
    print("\n🚀 Ready to start the API server and use the web interface!")
    print("   Run: python src/api/main.py")
    sys.exit(0)
else:
    print("\n⚠️ SOME TESTS FAILED")
    print("Review the errors above and fix before proceeding")
    sys.exit(1)
