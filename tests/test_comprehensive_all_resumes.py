"""
Comprehensive Test Suite - All Real Resumes
Tests semantic skill matching, quality scoring, and full matching pipeline
on 22 Overleaf + 50 GitHub = 72 real resumes
"""

import sys
import os
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, str(Path(__file__).parent))

from src.services.resume_parser import ResumeParser
from src.services.matching_engine import MatchingEngine
from src.ml.scorers.skill_matcher import SkillMatcher
from src.ml.resume_quality_scorer import ResumeQualityScorer
import json
from datetime import datetime


def test_all_resumes():
    """Test complete pipeline on all real resumes"""
    
    print("=" * 100)
    print("🧪 COMPREHENSIVE TEST SUITE - ALL REAL RESUMES")
    print("=" * 100)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Initialize components
    parser = ResumeParser(use_ml=True)
    quality_scorer = ResumeQualityScorer()
    skill_matcher = SkillMatcher(use_semantic=True, semantic_threshold=0.65)
    
    # Import experience classifier
    from src.ml.experience_classifier import ExperienceLevelClassifier
    experience_classifier = ExperienceLevelClassifier()
    
    # Get all resume paths
    overleaf_dir = Path('data/sample_resumes/overleaf_templates')
    github_dir = Path('data/sample_resumes/github_dataset')
    
    overleaf_resumes = list(overleaf_dir.glob('*.pdf'))
    github_resumes = [p for p in github_dir.glob('*.pdf') if p.is_file()]
    
    all_resumes = overleaf_resumes + github_resumes
    
    print(f"📁 Found Resumes:")
    print(f"   Overleaf templates: {len(overleaf_resumes)}")
    print(f"   GitHub dataset: {len(github_resumes)}")
    print(f"   Total: {len(all_resumes)}")
    
    # Statistics
    stats = {
        'total': len(all_resumes),
        'parsed_successfully': 0,
        'parsing_errors': 0,
        'with_names': 0,
        'with_skills': 0,
        'with_experience_level': 0,
        'quality_scores': [],
        'skill_counts': [],
        'experience_levels': [],
        'error_files': []
    }
    
    results = []
    
    print("\n" + "=" * 100)
    print("🔍 PARSING & ANALYZING ALL RESUMES...")
    print("=" * 100)
    
    for i, resume_path in enumerate(all_resumes, 1):
        print(f"\n[{i}/{len(all_resumes)}] {resume_path.name}")
        
        try:
            # Parse resume
            resume_data = parser.parse(str(resume_path))
            
            # Check if parsing succeeded
            if not resume_data or resume_data.get('error'):
                print(f"   ❌ Parsing failed: {resume_data.get('error', 'Unknown error')}")
                stats['parsing_errors'] += 1
                stats['error_files'].append(resume_path.name)
                continue
            
            stats['parsed_successfully'] += 1
            
            # Extract info
            name = resume_data.get('name', 'Unknown')
            
            # Handle skills extraction (nested structure)
            skills_data = resume_data.get('skills', {})
            if isinstance(skills_data, dict):
                skills = skills_data.get('all_skills', [])
            else:
                skills = skills_data if isinstance(skills_data, list) else []
            
            # Handle experience extraction (from sections or direct)
            experience = resume_data.get('experience', [])
            if not experience:
                # Try to get from sections
                sections = resume_data.get('sections', {})
                if sections:
                    exp_section = sections.get('experience', {})
                    if isinstance(exp_section, dict):
                        experience_text = exp_section.get('content', '')
                    else:
                        experience_text = ''
                else:
                    experience_text = ''
            else:
                experience_text = ' '.join([str(exp) for exp in experience])
            
            # Check name extraction
            if name and name != 'Unknown':
                stats['with_names'] += 1
                print(f"   ✅ Name: {name}")
            else:
                print(f"   ⚠️  Name: Not extracted")
            
            # Check skills
            if skills:
                stats['with_skills'] += 1
                skill_list = skills if isinstance(skills, list) else []
                stats['skill_counts'].append(len(skill_list))
                skill_preview = ', '.join([str(s) for s in skill_list[:5]]) if skill_list else 'N/A'
                print(f"   ✅ Skills: {len(skill_list)} found - {skill_preview}")
            else:
                print(f"   ⚠️  Skills: None extracted")
            
            # Score quality
            quality_result = quality_scorer.score_resume(resume_data)
            quality_score = quality_result['overall_score']
            quality_grade = quality_result['grade']
            stats['quality_scores'].append(quality_score)
            
            print(f"   ⭐ Quality: {quality_score:.1f}/10 ({quality_grade})")
            
            # Classify experience level
            experience_level = "Unknown"
            experience_confidence = 0.0
            if experience_text and len(experience_text.strip()) > 0:
                experience_pred = experience_classifier.predict(experience_text)
                experience_level = experience_pred.get('level', 'Unknown')
                experience_confidence = experience_pred.get('confidence', 0.0)
                
                if experience_level != "Unknown":
                    stats['with_experience_level'] += 1
                    stats['experience_levels'].append(experience_level)
                    print(f"   👤 Experience: {experience_level} ({experience_confidence:.0%} confidence)")
                else:
                    print(f"   ⚠️  Experience: Could not classify")
            else:
                print(f"   ⚠️  Experience: No experience data")
            
            # Save result
            exp_count = len(experience) if isinstance(experience, list) else (1 if experience_text else 0)
            results.append({
                'file': resume_path.name,
                'name': name,
                'skills_count': len(skills) if isinstance(skills, list) else 0,
                'experience_count': exp_count,
                'quality_score': quality_score,
                'quality_grade': quality_grade,
                'experience_level': experience_level,
                'experience_confidence': experience_confidence,
                'parsed': True
            })
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            stats['parsing_errors'] += 1
            stats['error_files'].append(resume_path.name)
            results.append({
                'file': resume_path.name,
                'error': str(e),
                'parsed': False
            })
    
    # Calculate statistics
    print("\n" + "=" * 100)
    print("📊 OVERALL STATISTICS")
    print("=" * 100)
    
    success_rate = (stats['parsed_successfully'] / stats['total']) * 100
    name_extraction_rate = (stats['with_names'] / stats['parsed_successfully']) * 100 if stats['parsed_successfully'] > 0 else 0
    skill_extraction_rate = (stats['with_skills'] / stats['parsed_successfully']) * 100 if stats['parsed_successfully'] > 0 else 0
    
    print(f"\n📈 Parsing Results:")
    print(f"   Total Resumes: {stats['total']}")
    print(f"   ✅ Parsed Successfully: {stats['parsed_successfully']} ({success_rate:.1f}%)")
    print(f"   ❌ Parsing Errors: {stats['parsing_errors']}")
    
    print(f"\n🎯 Extraction Results:")
    print(f"   Names Extracted: {stats['with_names']}/{stats['parsed_successfully']} ({name_extraction_rate:.1f}%)")
    print(f"   Skills Extracted: {stats['with_skills']}/{stats['parsed_successfully']} ({skill_extraction_rate:.1f}%)")
    
    experience_extraction_rate = (stats['with_experience_level'] / stats['parsed_successfully']) * 100 if stats['parsed_successfully'] > 0 else 0
    print(f"   Experience Levels Classified: {stats['with_experience_level']}/{stats['parsed_successfully']} ({experience_extraction_rate:.1f}%)")
    
    if stats['skill_counts']:
        avg_skills = sum(stats['skill_counts']) / len(stats['skill_counts'])
        max_skills = max(stats['skill_counts'])
        min_skills = min(stats['skill_counts'])
        print(f"\n🛠️  Skill Statistics:")
        print(f"   Average Skills per Resume: {avg_skills:.1f}")
        print(f"   Max Skills: {max_skills}")
        print(f"   Min Skills: {min_skills}")
    
    if stats['quality_scores']:
        avg_quality = sum(stats['quality_scores']) / len(stats['quality_scores'])
        max_quality = max(stats['quality_scores'])
        min_quality = min(stats['quality_scores'])
        
        # Grade distribution
        grade_counts = {}
        for result in results:
            if result.get('parsed'):
                grade = result['quality_grade'].split('(')[0].strip()
                grade_counts[grade] = grade_counts.get(grade, 0) + 1
        
        print(f"\n⭐ Quality Statistics:")
        print(f"   Average Quality: {avg_quality:.1f}/10")
        print(f"   Highest Quality: {max_quality:.1f}/10")
        print(f"   Lowest Quality: {min_quality:.1f}/10")
        print(f"\n   Grade Distribution:")
        for grade in ['A+', 'A', 'B+', 'B', 'C', 'D', 'F']:
            count = grade_counts.get(grade, 0)
            if count > 0:
                percentage = (count / len(stats['quality_scores'])) * 100
                print(f"     {grade}: {count} resumes ({percentage:.1f}%)")
    
    # Experience level distribution
    if stats['experience_levels']:
        print(f"\n👤 Experience Level Distribution:")
        level_counts = {}
        for level in stats['experience_levels']:
            level_counts[level] = level_counts.get(level, 0) + 1
        
        for level in ['Entry', 'Mid', 'Senior', 'Expert']:
            count = level_counts.get(level, 0)
            if count > 0:
                percentage = (count / len(stats['experience_levels'])) * 100
                print(f"     {level}: {count} resumes ({percentage:.1f}%)")
    
    # Show error files if any
    if stats['error_files']:
        print(f"\n⚠️  Files with Errors ({len(stats['error_files'])}):")
        for filename in stats['error_files'][:10]:  # Show first 10
            print(f"     • {filename}")
        if len(stats['error_files']) > 10:
            print(f"     ... and {len(stats['error_files']) - 10} more")
    
    # Top quality resumes
    print(f"\n🏆 TOP 10 QUALITY RESUMES:")
    sorted_results = sorted([r for r in results if r.get('parsed')], 
                          key=lambda x: x['quality_score'], reverse=True)
    for i, result in enumerate(sorted_results[:10], 1):
        print(f"   {i}. {result['file']}")
        print(f"      Score: {result['quality_score']:.1f}/10 ({result['quality_grade']})")
        print(f"      Name: {result['name']}, Skills: {result['skills_count']}")
        print(f"      Experience: {result.get('experience_level', 'Unknown')} ({result.get('experience_confidence', 0):.0%})")
    
    # Save detailed results
    output_file = Path('test_results') / f'comprehensive_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'statistics': stats,
            'results': results
        }, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {output_file}")
    
    print("\n" + "=" * 100)
    print("✅ COMPREHENSIVE TEST COMPLETE")
    print("=" * 100)
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return stats, results


def test_semantic_matching_on_real_resumes():
    """Test semantic skill matching on real resumes"""
    
    print("\n" + "=" * 100)
    print("🔍 SEMANTIC SKILL MATCHING TEST - Real Resumes")
    print("=" * 100)
    
    parser = ResumeParser(use_ml=True)
    skill_matcher = SkillMatcher(use_semantic=True, semantic_threshold=0.65)
    
    # Test with a few resumes
    test_dir = Path('data/sample_resumes/overleaf_templates')
    test_files = list(test_dir.glob('*.pdf'))[:5]  # Test first 5
    
    # Sample job requirements
    job_skills = {
        'required': ['Python', 'Machine Learning', 'Deep Learning', 'TensorFlow'],
        'optional': ['AWS', 'Docker', 'Kubernetes']
    }
    
    print(f"\n📋 Job Requirements:")
    print(f"   Required: {', '.join(job_skills['required'])}")
    print(f"   Optional: {', '.join(job_skills['optional'])}")
    
    for i, resume_path in enumerate(test_files, 1):
        print(f"\n{'─' * 100}")
        print(f"[{i}/{len(test_files)}] Testing: {resume_path.name}")
        print(f"{'─' * 100}")
        
        try:
            # Parse resume
            resume_data = parser.parse(str(resume_path))
            
            # Extract skills properly
            skills_data = resume_data.get('skills', {})
            if isinstance(skills_data, dict):
                skill_list = skills_data.get('all_skills', [])
            else:
                skill_list = skills_data if isinstance(skills_data, list) else []
            
            skill_preview = ', '.join([str(s) for s in skill_list[:8]]) if skill_list else 'None'
            
            print(f"   Candidate Skills ({len(skill_list)}): {skill_preview}")
            
            # Test semantic matching
            match_result = skill_matcher.calculate_match_score(
                skill_list,
                job_skills['required'],
                job_skills['optional']
            )
            
            print(f"\n   📊 Match Results:")
            print(f"      Score: {match_result['score']:.1f}/100")
            print(f"      Required Matched: {len(match_result['required_matches'])}/{match_result['total_required']}")
            print(f"      Optional Matched: {len(match_result['optional_matches'])}/{match_result['total_optional']}")
            
            if match_result.get('semantic_details'):
                print(f"\n   🔍 Semantic Matches:")
                for skill, details in list(match_result['semantic_details']['required'].items())[:5]:
                    print(f"      '{skill}' ≈ '{details['matched_with']}' ({details['similarity']:.0%})")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "=" * 100)


if __name__ == "__main__":
    # Run comprehensive test
    stats, results = test_all_resumes()
    
    # Run semantic matching test
    test_semantic_matching_on_real_resumes()
