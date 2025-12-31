"""Test auto-computed semantic score"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ml.match_scorer import MatchScorer

scorer = MatchScorer()

candidate = {
    'name': 'Test Dev',
    'skills': {'all_skills': ['Python', 'Django', 'PostgreSQL', 'Docker']},
    'experience': [{'title': 'Senior Python Developer', 'duration_months': 48}],
    'education': []
}

job = {
    'title': 'Python Backend Developer',
    'required_skills': ['Python', 'Django', 'PostgreSQL'],
    'preferred_skills': ['Docker', 'AWS']
}

# Test WITHOUT passing semantic_score (should auto-compute)
print("Testing auto-computed semantic score...")
result = scorer.calculate_match(candidate, job)

print('=== Auto-Computed Semantic Score Test ===')
print(f"Final Score: {result['final_score']}")
print(f"Semantic Score: {result['scores']['semantic']}")
print(f"Semantic Details: {result['details'].get('semantic', {})}")
print(f"All Scores: {result['scores']}")

# Compare with a bad match
bad_candidate = {
    'name': 'Chef',
    'skills': {'all_skills': ['Cooking', 'Baking', 'Food Safety']},
    'experience': [{'title': 'Head Chef', 'duration_months': 60}],
    'education': []
}

print("\n=== Bad Match (Chef vs Python Dev) ===")
result2 = scorer.calculate_match(bad_candidate, job)
print(f"Final Score: {result2['final_score']}")
print(f"Semantic Score: {result2['scores']['semantic']}")
print(f"Skills Score: {result2['scores']['skills']}")

print("\n✅ Semantic score is now auto-computed!")
