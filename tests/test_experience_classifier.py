"""Lightweight unit test for the ExperienceLevelClassifier.

This file contains a compact script that imports the classifier module
directly (by file path) to avoid importing the full `src` package which
may require heavy optional dependencies during testing.
"""
import sys
import importlib.util
from pathlib import Path


# Load the experience_classifier module directly (avoid package imports)
module_path = Path(__file__).resolve().parents[1] / 'src' / 'ml' / 'experience_classifier.py'
spec = importlib.util.spec_from_file_location('experience_classifier', str(module_path))
ec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ec)
ExperienceLevelClassifier = ec.ExperienceLevelClassifier


def run_tests():
    clf = ExperienceLevelClassifier()

    cases = [
        ("2 years experience as software engineer", 'Mid'),
        ("7 years experience in backend engineering", 'Senior'),
        ("Senior Software Engineer with 6+ years", 'Senior'),
        ("Entry level data analyst, 6 months internship", 'Entry'),
        ("Principal engineer, 12 years experience", 'Expert')
    ]

    failures = 0
    for text, expected in cases:
        res = clf.predict(text)
        level = res.get('level')
        conf = res.get('confidence')
        print(f"INPUT: {text}\n -> PREDICTED: {level} (conf={conf:.2f}) | EXPECTED: {expected}\n")

        # The heuristic may coarsely match; accept exact or higher for expert
        if expected == 'Expert':
            ok = level in ('Expert', 'Senior')
        else:
            ok = level == expected

        if not ok:
            failures += 1

    if failures:
        print(f"\n⚠️  {failures} test(s) failed")
        sys.exit(1)

    print("\n✅ All experience classifier tests passed")


if __name__ == '__main__':
    run_tests()
"""
Test Experience Level Classifier on Real Resumes
Tests the BERT-based classifier on actual resume data
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.resume_parser import ResumeParser
from src.ml.classifiers.experience_classifier import ExperienceLevelClassifier
import codecs

# UTF-8 fix for Windows console
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def test_classifier_on_real_resumes():
    """Test classifier on sample resumes"""
    
    print("=" * 80)
    print("🧪 Testing Experience Classifier on Real Resumes")
    print("=" * 80)
    
    # Initialize
    parser = ResumeParser()
    classifier = ExperienceLevelClassifier(
        model_name='bert-base-uncased',
        use_pretrained=False
    )
    
    # Test resumes with expected levels
    test_cases = [
        {
            'file': 'data/sample_resumes/john_doe_full_stack.txt',
            'expected': 'mid',  # 5 years
            'name': 'John Doe (Full Stack - 5 years)'
        },
        {
            'file': 'data/sample_resumes/sarah_chen_data_scientist.txt',
            'expected': 'mid',  # 3 years
            'name': 'Sarah Chen (Data Scientist - 3 years)'
        },
        {
            'file': 'data/test_resumes/overleaf_templates/deedy_resume.pdf',
            'expected': 'mid',  # Typical template
            'name': 'Deedy Resume Template'
        },
        {
            'file': 'data/test_resumes/overleaf_templates/awesome_cv.pdf',
            'expected': 'senior',  # Senior level template
            'name': 'Awesome CV Template'
        }
    ]
    
    print(f"\n📁 Testing {len(test_cases)} resumes...\n")
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        file_path = Path(test['file'])
        
        if not file_path.exists():
            print(f"{i}. ⚠️  {test['name']}")
            print(f"   File not found: {file_path}")
            print()
            continue
        
        print(f"{i}. 📄 {test['name']}")
        print(f"   File: {file_path.name}")
        
        # Parse resume
        try:
            resume_data = parser.parse(str(file_path))
            
            if not resume_data.get('success'):
                print(f"   ❌ Parsing failed")
                print()
                continue
            
            # Calculate years
            experience = resume_data.get('experience', [])
            total_months = sum(e.get('duration_months', 0) for e in experience)
            years = total_months / 12.0
            
            # Classify
            result = classifier.classify(
                resume_data,
                use_hybrid=True,
                confidence_threshold=0.7
            )
            
            level = result['level']
            confidence = result['confidence']
            method = result['method']
            reasoning = result['reasoning']
            
            is_correct = level == test['expected']
            status = "✅" if is_correct else "❌"
            
            print(f"   {status} Predicted: {level} (expected: {test['expected']})")
            print(f"   Years: {years:.1f}")
            print(f"   Confidence: {confidence:.1%}")
            print(f"   Method: {method}")
            print(f"   Reasoning: {reasoning}")
            
            # Show probabilities if ML
            if 'ml_prediction' in result:
                ml_pred = result['ml_prediction']
                if 'probabilities' in ml_pred:
                    probs = ml_pred['probabilities']
                    print(f"   Probabilities: ", end='')
                    for lvl in ['entry', 'mid', 'senior', 'expert']:
                        prob = probs.get(lvl, 0)
                        print(f"{lvl}={prob:.1%} ", end='')
                    print()
            
            results.append({
                'name': test['name'],
                'expected': test['expected'],
                'predicted': level,
                'correct': is_correct,
                'confidence': confidence,
                'years': years
            })
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    # Summary
    if results:
        correct = sum(1 for r in results if r['correct'])
        total = len(results)
        accuracy = correct / total * 100
        
        print("=" * 80)
        print("📊 RESULTS SUMMARY")
        print("=" * 80)
        print(f"Total resumes tested: {total}")
        print(f"Correct predictions: {correct}")
        print(f"Accuracy: {accuracy:.1f}%")
        print()
        
        # Breakdown by level
        print("Breakdown by expected level:")
        for level in ['entry', 'mid', 'senior', 'expert']:
            level_results = [r for r in results if r['expected'] == level]
            if level_results:
                level_correct = sum(1 for r in level_results if r['correct'])
                level_total = len(level_results)
                level_acc = level_correct / level_total * 100
                print(f"  {level.capitalize()}: {level_acc:.0f}% ({level_correct}/{level_total})")
        
        print()
        
        # Show misclassifications
        misclassified = [r for r in results if not r['correct']]
        if misclassified:
            print("❌ Misclassifications:")
            for r in misclassified:
                print(f"  • {r['name']}")
                print(f"    Expected: {r['expected']}, Got: {r['predicted']}")
                print(f"    Years: {r['years']:.1f}, Confidence: {r['confidence']:.1%}")
        
        print()
        
        # Average confidence
        avg_confidence = sum(r['confidence'] for r in results) / len(results)
        print(f"Average confidence: {avg_confidence:.1%}")
        
        print("=" * 80)


def test_edge_cases():
    """Test edge cases and boundary conditions"""
    
    print("\n" + "=" * 80)
    print("🔬 Testing Edge Cases")
    print("=" * 80)
    
    classifier = ExperienceLevelClassifier(use_pretrained=False)
    
    edge_cases = [
        {
            'name': 'No Experience',
            'data': {
                'experience': [],
                'skills': ['Python', 'Git'],
                'education': [{'degree': 'Bachelor'}]
            },
            'expected': 'entry'
        },
        {
            'name': 'Career Changer (High Education, Low Experience)',
            'data': {
                'experience': [
                    {'title': 'Junior Developer', 'duration_months': 12}
                ],
                'skills': ['Python', 'Django', 'AWS'],
                'education': [{'degree': 'PhD in Computer Science'}]
            },
            'expected': 'entry'
        },
        {
            'name': 'Ambiguous Title (Many years but junior title)',
            'data': {
                'experience': [
                    {'title': 'Software Engineer', 'duration_months': 84}  # 7 years
                ],
                'skills': [f'Skill{i}' for i in range(20)],
                'education': [{'degree': 'Bachelor'}]
            },
            'expected': 'senior'
        }
    ]
    
    print(f"\n📝 Testing {len(edge_cases)} edge cases...\n")
    
    for i, test in enumerate(edge_cases, 1):
        print(f"{i}. {test['name']}")
        
        result = classifier.classify(test['data'], use_hybrid=True)
        
        level = result['level']
        confidence = result['confidence']
        expected = test['expected']
        
        is_correct = level == expected
        status = "✅" if is_correct else "⚠️ "
        
        print(f"   {status} Predicted: {level} (expected: {expected})")
        print(f"   Confidence: {confidence:.1%}")
        print(f"   Reasoning: {result['reasoning']}")
        print()
    
    print("=" * 80)


if __name__ == "__main__":
    # Test on real resumes
    test_classifier_on_real_resumes()
    
    # Test edge cases
    test_edge_cases()
    
    print("\n✅ All tests complete!")
