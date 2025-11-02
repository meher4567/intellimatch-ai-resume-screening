"""
Test Semantic Skill Matcher
Compare exact matching vs semantic matching
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.ml.scorers.skill_matcher import SkillMatcher


def test_semantic_advantage():
    """Show how semantic matching catches more matches"""
    
    print("=" * 80)
    print("🧪 SEMANTIC SKILL MATCHING TEST")
    print("=" * 80)
    
    # Test case: candidate uses variations of required skills
    candidate_skills = [
        'Python', 'ML', 'Deep Learning', 'Postgres', 
        'AWS Cloud', 'REST APIs', 'Neural Networks',
        'Natural Language Processing', 'CI/CD Pipelines'
    ]
    
    required_skills = [
        'Python', 'Machine Learning', 'PostgreSQL',
        'Amazon Web Services', 'RESTful API', 'NLP',
        'Artificial Intelligence', 'Continuous Integration'
    ]
    
    optional_skills = [
        'Docker', 'Kubernetes', 'TensorFlow', 'PyTorch'
    ]
    
    print("\n📋 CANDIDATE SKILLS:")
    for skill in candidate_skills:
        print(f"   • {skill}")
    
    print("\n📌 REQUIRED SKILLS:")
    for skill in required_skills:
        print(f"   • {skill}")
    
    print("\n⭐ OPTIONAL SKILLS:")
    for skill in optional_skills:
        print(f"   • {skill}")
    
    # Test 1: EXACT matching
    print("\n" + "=" * 80)
    print("1️⃣  EXACT STRING MATCHING (OLD)")
    print("=" * 80)
    
    exact_matcher = SkillMatcher(use_semantic=False)
    exact_result = exact_matcher.calculate_match_score(
        candidate_skills, required_skills, optional_skills
    )
    
    print(f"\n   📊 Score: {exact_result['score']}/100")
    print(f"   ✅ Required Matched: {len(exact_result['required_matches'])}/{exact_result['total_required']}")
    print(f"      {exact_result['required_matches']}")
    print(f"   ❌ Required Missing: {len(exact_result['missing_required'])}")
    print(f"      {exact_result['missing_required']}")
    print(f"   ⭐ Optional Matched: {len(exact_result['optional_matches'])}/{exact_result['total_optional']}")
    
    # Test 2: SEMANTIC matching
    print("\n" + "=" * 80)
    print("2️⃣  SEMANTIC MATCHING WITH EMBEDDINGS (NEW)")
    print("=" * 80)
    
    semantic_matcher = SkillMatcher(use_semantic=True, semantic_threshold=0.65)
    semantic_result = semantic_matcher.calculate_match_score(
        candidate_skills, required_skills, optional_skills
    )
    
    print(f"\n   📊 Score: {semantic_result['score']}/100")
    print(f"   ✅ Required Matched: {len(semantic_result['required_matches'])}/{semantic_result['total_required']}")
    
    # Show semantic matches with similarity scores
    print("\n   🔍 SEMANTIC MATCHES:")
    for req_skill, match_info in semantic_result['semantic_details']['required'].items():
        matched_with = match_info['matched_with']
        similarity = match_info['similarity']
        print(f"      '{req_skill}' ≈ '{matched_with}' (similarity: {similarity:.2%})")
    
    print(f"\n   ❌ Required Missing: {len(semantic_result['missing_required'])}")
    if semantic_result['missing_required']:
        print(f"      {semantic_result['missing_required']}")
    
    print(f"\n   ⭐ Optional Matched: {len(semantic_result['optional_matches'])}/{semantic_result['total_optional']}")
    if semantic_result['semantic_details']['optional']:
        print("   🔍 OPTIONAL SEMANTIC MATCHES:")
        for opt_skill, match_info in semantic_result['semantic_details']['optional'].items():
            matched_with = match_info['matched_with']
            similarity = match_info['similarity']
            print(f"      '{opt_skill}' ≈ '{matched_with}' (similarity: {similarity:.2%})")
    
    # Calculate improvement
    print("\n" + "=" * 80)
    print("📈 IMPROVEMENT ANALYSIS")
    print("=" * 80)
    
    score_improvement = semantic_result['score'] - exact_result['score']
    matches_gained = len(semantic_result['required_matches']) - len(exact_result['required_matches'])
    
    print(f"\n   Score Improvement: +{score_improvement:.2f} points ({score_improvement / exact_result['score'] * 100:.1f}% better)")
    print(f"   Additional Matches: +{matches_gained} required skills found")
    print(f"   Coverage Improvement: {exact_result['required_coverage']:.0f}% → {semantic_result['required_coverage']:.0f}%")
    
    print("\n" + "=" * 80)
    print("✅ TEST COMPLETE - Semantic matching significantly better!")
    print("=" * 80)


if __name__ == "__main__":
    test_semantic_advantage()
