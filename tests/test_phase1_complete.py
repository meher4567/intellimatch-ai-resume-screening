"""
Comprehensive Phase 1 Testing Suite
Tests all components and integration
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import json
from datetime import datetime

print("=" * 80)
print("🧪 PHASE 1 COMPREHENSIVE TESTING SUITE")
print("=" * 80)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Test results tracker
test_results = {
    'passed': [],
    'failed': [],
    'warnings': []
}

def test_section(name):
    """Decorator for test sections"""
    def decorator(func):
        def wrapper():
            print(f"\n{'=' * 80}")
            print(f"📋 TEST SECTION: {name}")
            print('=' * 80)
            try:
                func()
                test_results['passed'].append(name)
                print(f"✅ {name} - PASSED")
            except Exception as e:
                test_results['failed'].append((name, str(e)))
                print(f"❌ {name} - FAILED: {e}")
                import traceback
                traceback.print_exc()
        return wrapper
    return decorator


# ============================================================================
# TEST 1: Module Imports
# ============================================================================

@test_section("1. Module Imports")
def test_imports():
    print("\n📦 Testing imports...")
    
    modules = [
        ("Embedding Generator", "src.ml.embedding_generator", "EmbeddingGenerator"),
        ("Vector Store", "src.ml.vector_store", "VectorStore"),
        ("Semantic Search", "src.ml.semantic_search", "SemanticSearch"),
        ("Skill Matcher", "src.ml.scorers.skill_matcher", "SkillMatcher"),
        ("Experience Matcher", "src.ml.scorers.experience_matcher", "ExperienceMatcher"),
        ("Education Matcher", "src.ml.scorers.education_matcher", "EducationMatcher"),
        ("Match Scorer", "src.ml.match_scorer", "MatchScorer"),
        ("Candidate Ranker", "src.ml.candidate_ranker", "CandidateRanker"),
        ("Match Explainer", "src.ml.match_explainer", "MatchExplainer"),
        ("Matching Engine", "src.services.matching_engine", "MatchingEngine"),
        ("Job Parser", "src.services.job_description_parser", "JobDescriptionParser"),
        ("Resume Parser", "src.services.resume_parser", "ResumeParser"),
    ]
    
    for name, module_path, class_name in modules:
        try:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"   ✅ {name}: {cls.__name__}")
        except Exception as e:
            raise Exception(f"Failed to import {name}: {e}")
    
    print(f"\n   ✅ All {len(modules)} modules imported successfully!")


# ============================================================================
# TEST 2: Skill Matcher
# ============================================================================

@test_section("2. Skill Matcher")
def test_skill_matcher():
    from src.ml.scorers.skill_matcher import SkillMatcher
    
    print("\n🎯 Testing skill matching...")
    matcher = SkillMatcher()
    
    # Test 1: Exact match
    candidate_data = {'skills': {'all_skills': ['Python', 'Django', 'PostgreSQL']}}
    job_data = {'required_skills': ['Python', 'Django']}
    score = matcher.calculate_match_score(candidate_data, job_data)
    print(f"   Test 1 - Exact match: {score:.2f} (expected: >0.9)")
    assert score > 0.9, f"Exact match should score >0.9, got {score}"
    
    # Test 2: Synonym match
    candidate_data = {'skills': {'all_skills': ['JavaScript', 'React', 'Node.js']}}
    job_data = {'required_skills': ['JS', 'ReactJS']}
    score = matcher.calculate_match_score(candidate_data, job_data)
    print(f"   Test 2 - Synonym match: {score:.2f} (expected: >0.6)")
    assert score > 0.6, f"Synonym match should score >0.6, got {score}"
    
    # Test 3: No match
    candidate_data = {'skills': {'all_skills': ['Python', 'Django']}}
    job_data = {'required_skills': ['Java', 'Spring']}
    score = matcher.calculate_match_score(candidate_data, job_data)
    print(f"   Test 3 - No match: {score:.2f} (expected: <0.3)")
    assert score < 0.3, f"No match should score <0.3, got {score}"
    
    print("   ✅ All skill matcher tests passed!")


# ============================================================================
# TEST 3: Experience Matcher
# ============================================================================

@test_section("3. Experience Matcher")
def test_experience_matcher():
    from src.ml.scorers.experience_matcher import ExperienceMatcher
    
    print("\n💼 Testing experience matching...")
    matcher = ExperienceMatcher()
    
    # Test 1: Sufficient experience
    candidate_data = {
        'experience': [
            {'title': 'Senior Developer', 'duration_months': 48, 'achievements': ['Led team']},
            {'title': 'Developer', 'duration_months': 24, 'achievements': ['Built API']}
        ]
    }
    job_data = {'required_experience_years': 3}
    score = matcher.calculate_match_score(candidate_data, job_data)
    print(f"   Test 1 - Sufficient experience (6y vs 3y req): {score:.2f}")
    assert score > 0.8, f"Sufficient experience should score >0.8, got {score}"
    
    # Test 2: Exact requirement
    candidate_data = {'experience': [{'title': 'Developer', 'duration_months': 36, 'achievements': []}]}
    job_data = {'required_experience_years': 3}
    score = matcher.calculate_match_score(candidate_data, job_data)
    print(f"   Test 2 - Exact requirement (3y vs 3y req): {score:.2f}")
    assert score > 0.7, f"Exact requirement should score >0.7, got {score}"
    
    # Test 3: Insufficient experience
    candidate_data = {'experience': [{'title': 'Junior Dev', 'duration_months': 12, 'achievements': []}]}
    job_data = {'required_experience_years': 5}
    score = matcher.calculate_match_score(candidate_data, job_data)
    print(f"   Test 3 - Insufficient experience (1y vs 5y req): {score:.2f}")
    assert score < 0.5, f"Insufficient experience should score <0.5, got {score}"
    
    print("   ✅ All experience matcher tests passed!")


# ============================================================================
# TEST 4: Education Matcher
# ============================================================================

@test_section("4. Education Matcher")
def test_education_matcher():
    from src.ml.scorers.education_matcher import EducationMatcher
    
    print("\n🎓 Testing education matching...")
    matcher = EducationMatcher()
    
    # Test 1: Perfect match
    candidate_data = {
        'education': [
            {'degree': 'Bachelor of Science', 'field_of_study': 'Computer Science', 
             'institution': 'MIT'}
        ]
    }
    job_data = {'education_level': 'Bachelor'}
    score = matcher.calculate_match_score(candidate_data, job_data)
    print(f"   Test 1 - Perfect match (BS CS): {score:.2f}")
    assert score > 0.7, f"Perfect match should score >0.7, got {score}"
    
    # Test 2: Higher degree
    candidate_data = {
        'education': [
            {'degree': 'Master of Science', 'field_of_study': 'Data Science'}
        ]
    }
    job_data = {'education_level': 'Bachelor'}
    score = matcher.calculate_match_score(candidate_data, job_data)
    print(f"   Test 2 - Higher degree (MS vs BS req): {score:.2f}")
    assert score > 0.7, f"Higher degree should score >0.7, got {score}"
    
    print("   ✅ All education matcher tests passed!")


# ============================================================================
# TEST 5: Match Scorer (Integration)
# ============================================================================

@test_section("5. Match Scorer")
def test_match_scorer():
    from src.ml.match_scorer import MatchScorer
    
    print("\n📊 Testing match scoring...")
    scorer = MatchScorer()
    
    # Test comprehensive scoring
    resume_data = {
        'skills': {
            'all_skills': ['Python', 'Django', 'AWS', 'PostgreSQL'],
            'top_skills': ['Python', 'Django', 'AWS']
        },
        'experience': [
            {'title': 'Senior Developer', 'duration_months': 48, 
             'achievements': ['Led team', 'Built scalable systems']}
        ],
        'education': [
            {'degree': 'Bachelor of Science', 'field_of_study': 'Computer Science'}
        ]
    }
    
    job_data = {
        'required_skills': ['Python', 'Django', 'AWS'],
        'required_experience': {'min_years': 3},
        'required_education': {'degree_level': 'Bachelor', 'field': 'Computer Science'}
    }
    
    result = scorer.calculate_match(candidate_data=resume_data, job_data=job_data, semantic_score=0.85)
    
    print(f"   Overall score: {result['final_score']:.2f}/100")
    print(f"   - Skills: {result['component_scores']['skills']:.2f}")
    print(f"   - Experience: {result['component_scores']['experience']:.2f}")
    print(f"   - Education: {result['component_scores']['education']:.2f}")
    
    assert result['final_score'] > 60, f"Good match should score >60, got {result['final_score']}"
    assert result['component_scores']['skills'] > 0.7, "Skills should score reasonably"
    
    print("   ✅ Match scorer test passed!")


# ============================================================================
# TEST 6: Candidate Ranker
# ============================================================================

@test_section("6. Candidate Ranker")
def test_candidate_ranker():
    from src.ml.candidate_ranker import CandidateRanker
    
    print("\n🏆 Testing candidate ranking...")
    ranker = CandidateRanker()
    
    # Create test candidates
    candidates = [
        {'name': 'Alice', 'match_score': 95, 'resume_id': '1'},
        {'name': 'Bob', 'match_score': 75, 'resume_id': '2'},
        {'name': 'Charlie', 'match_score': 55, 'resume_id': '3'},
        {'name': 'David', 'match_score': 85, 'resume_id': '4'},
    ]
    
    ranked = ranker.rank_candidates(candidates)
    
    print(f"   Ranked {len(ranked)} candidates:")
    for i, candidate in enumerate(ranked, 1):
        print(f"   {i}. {candidate['name']}: {candidate['match_score']}/100 ({candidate['tier']}-Tier)")
    
    # Verify ranking order
    assert ranked[0]['name'] == 'Alice', "Highest score should be first"
    assert ranked[0]['tier'] == 'S', "95 should be S-tier"
    assert ranked[1]['name'] == 'David', "Second highest should be David"
    assert ranked[1]['tier'] == 'A', "85 should be A-tier"
    assert ranked[2]['tier'] == 'B', "75 should be B-tier"
    assert ranked[3]['tier'] == 'D', "55 should be D-tier"
    
    print("   ✅ Candidate ranker test passed!")


# ============================================================================
# TEST 7: Match Explainer
# ============================================================================

@test_section("7. Match Explainer")
def test_match_explainer():
    from src.ml.match_explainer import MatchExplainer
    
    print("\n💡 Testing match explanation...")
    explainer = MatchExplainer()
    
    match_data = {
        'resume_id': 'test_resume',
        'name': 'John Doe',
        'final_score': 85.5,
        'tier': 'A',
        'component_scores': {
            'skills': 0.90,
            'experience': 0.85,
            'education': 0.75,
            'quality': 0.95
        }
    }
    
    job_data = {
        'title': 'Senior Python Developer',
        'required_skills': ['Python', 'Django', 'AWS']
    }
    
    explanation = explainer.explain_match(match_data)
    
    print(f"   Summary: {explanation['summary'][:100]}...")
    print(f"   Strengths: {len(explanation['strengths'])} found")
    print(f"   Weaknesses: {len(explanation['weaknesses'])} found")
    
    assert 'summary' in explanation, "Should have summary"
    assert 'strengths' in explanation, "Should have strengths"
    assert 'recommendation' in explanation, "Should have recommendation"
    
    print("   ✅ Match explainer test passed!")


# ============================================================================
# TEST 8: Matching Engine (End-to-End)
# ============================================================================

@test_section("8. Matching Engine (End-to-End)")
def test_matching_engine():
    from src.services.matching_engine import MatchingEngine
    
    print("\n🚀 Testing full matching pipeline...")
    engine = MatchingEngine(model_name='mini')
    
    # Test resume data
    test_resumes = [
        {
            'metadata': {'file_name': 'alice.pdf', 'quality_score': 95},
            'personal_info': {'name': 'Alice Johnson', 'email': 'alice@example.com'},
            'skills': {
                'all_skills': ['Python', 'Django', 'AWS', 'PostgreSQL', 'Docker'],
                'top_skills': ['Python', 'Django', 'AWS']
            },
            'experience': [
                {'title': 'Senior Software Engineer', 'company': 'TechCorp', 
                 'duration_months': 48, 'achievements': ['Led team of 5', 'Built scalable APIs']}
            ],
            'education': [
                {'degree': 'Bachelor of Science', 'field_of_study': 'Computer Science', 
                 'institution': 'MIT'}
            ]
        },
        {
            'metadata': {'file_name': 'bob.pdf', 'quality_score': 80},
            'personal_info': {'name': 'Bob Smith', 'email': 'bob@example.com'},
            'skills': {
                'all_skills': ['Java', 'Spring', 'MySQL'],
                'top_skills': ['Java', 'Spring']
            },
            'experience': [
                {'title': 'Java Developer', 'company': 'JavaCo', 
                 'duration_months': 24, 'achievements': ['Built microservices']}
            ],
            'education': [
                {'degree': 'Bachelor', 'field_of_study': 'IT', 'institution': 'State U'}
            ]
        }
    ]
    
    print("\n   Step 1: Indexing resumes...")
    resume_ids = engine.index_resumes_batch(test_resumes)
    print(f"   ✅ Indexed {len(resume_ids)} resumes: {resume_ids}")
    
    print("\n   Step 2: Parsing job description...")
    job_text = """
    Senior Python Developer needed. 
    Must have 3+ years experience with Python, Django, and AWS.
    Bachelor's degree in Computer Science required.
    """
    job_data = engine.parse_job(job_text)
    print(f"   ✅ Job parsed")
    
    print("\n   Step 3: Finding matches...")
    matches = engine.find_matches(job_data, top_k=2)
    print(f"   ✅ Found {len(matches)} matches")
    
    for i, match in enumerate(matches, 1):
        print(f"\n   Match {i}: {match['name']}")
        print(f"   - Score: {match['match_score']:.2f}/100")
        print(f"   - Tier: {match['tier']}")
        if 'explanation' in match:
            print(f"   - Summary: {match['explanation']['summary'][:80]}...")
    
    # Verify results
    assert len(matches) > 0, "Should find at least one match"
    assert matches[0]['name'] == 'Alice Johnson', "Alice should be top match"
    assert matches[0]['match_score'] > 50, "Top match should have decent score"
    
    print("\n   ✅ End-to-end pipeline test passed!")


# ============================================================================
# TEST 9: File Structure
# ============================================================================

@test_section("9. File Structure")
def test_file_structure():
    print("\n📁 Verifying file structure...")
    
    required_files = {
        'Core ML': [
            'src/ml/embedding_generator.py',
            'src/ml/vector_store.py',
            'src/ml/semantic_search.py',
        ],
        'Scorers': [
            'src/ml/scorers/skill_matcher.py',
            'src/ml/scorers/experience_matcher.py',
            'src/ml/scorers/education_matcher.py',
        ],
        'Integration': [
            'src/ml/match_scorer.py',
            'src/ml/candidate_ranker.py',
            'src/ml/match_explainer.py',
        ],
        'Services': [
            'src/services/matching_engine.py',
            'src/services/job_description_parser.py',
            'src/services/resume_parser.py',
        ],
        'API & Frontend': [
            'src/api/main.py',
            'frontend/index.html',
        ],
        'Documentation': [
            'QUICKSTART.md',
            'PHASE1_COMPLETION_REPORT.md',
        ]
    }
    
    total_files = 0
    found_files = 0
    
    for category, files in required_files.items():
        print(f"\n   {category}:")
        for file_path in files:
            total_files += 1
            full_path = Path(file_path)
            if full_path.exists():
                found_files += 1
                print(f"   ✅ {file_path}")
            else:
                print(f"   ❌ {file_path} - MISSING")
                raise FileNotFoundError(f"Required file missing: {file_path}")
    
    print(f"\n   ✅ All {found_files}/{total_files} required files present!")


# ============================================================================
# RUN ALL TESTS
# ============================================================================

if __name__ == "__main__":
    test_imports()
    test_skill_matcher()
    test_experience_matcher()
    test_education_matcher()
    test_match_scorer()
    test_candidate_ranker()
    test_match_explainer()
    test_matching_engine()
    test_file_structure()
    
    # Final report
    print("\n" + "=" * 80)
    print("📊 FINAL TEST REPORT")
    print("=" * 80)
    
    total_tests = len(test_results['passed']) + len(test_results['failed'])
    passed = len(test_results['passed'])
    failed = len(test_results['failed'])
    
    print(f"\n✅ Passed: {passed}/{total_tests}")
    if test_results['passed']:
        for test in test_results['passed']:
            print(f"   ✅ {test}")
    
    if failed > 0:
        print(f"\n❌ Failed: {failed}/{total_tests}")
        for test, error in test_results['failed']:
            print(f"   ❌ {test}")
            print(f"      Error: {error}")
    
    if test_results['warnings']:
        print(f"\n⚠️  Warnings: {len(test_results['warnings'])}")
        for warning in test_results['warnings']:
            print(f"   ⚠️  {warning}")
    
    print("\n" + "=" * 80)
    if failed == 0:
        print("🎉 ALL TESTS PASSED - PHASE 1 COMPLETE!")
    else:
        print("⚠️  SOME TESTS FAILED - NEEDS ATTENTION")
    print("=" * 80)
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    sys.exit(0 if failed == 0 else 1)
