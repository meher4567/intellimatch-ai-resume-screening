"""Phase 1 pipeline wrapper

A defensive, lightweight orchestration layer that calls available Phase 1 modules
and produces a canonical JSON-like dict. It's intentionally permissive: when a
module or function isn't present it will skip it and include a note in the output.

This is meant as a smoke-test and integration adapter; later we can tighten
contracts and replace fallbacks with strict imports.
"""
from typing import Dict, Any, Optional
import traceback
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Initialize module instances
quality_scorer = None
context_skill_extractor = None
timeline_analyzer = None
question_generator = None
bias_detector = None
ml_support = None

# Defensive imports - instantiate classes where needed
try:
    from src.ml.resume_quality_scorer import ResumeQualityScorer
    quality_scorer = ResumeQualityScorer()
except Exception as e:
    print(f"Warning: Could not import ResumeQualityScorer: {e}")

try:
    from src.ml.context_aware_skill_extractor import extract_contextual_skills as context_skill_extractor
except Exception as e:
    print(f"Warning: Could not import context_aware_skill_extractor: {e}")

# ESCO Skills Validation
esco_mapper = None
skill_validator = None
try:
    from src.ml.esco_skill_mapper import ESCOSkillMapper, SkillValidator
    esco_mapper = ESCOSkillMapper()
    skill_validator = SkillValidator(esco_mapper)
except Exception as e:
    print(f"Warning: Could not import ESCO mapper: {e}")

try:
    from src.ml.experience_timeline_analyzer import ExperienceTimelineAnalyzer
    timeline_analyzer_inst = ExperienceTimelineAnalyzer()
    # The class method expects experience_data list, but we'll pass whole resume
    # and extract experience field inside our wrapper
    timeline_analyzer = timeline_analyzer_inst
except Exception as e:
    print(f"Warning: Could not import experience_timeline_analyzer: {e}")
    timeline_analyzer = None

try:
    from src.ml.interview_question_generator import InterviewQuestionGenerator
    question_generator = InterviewQuestionGenerator()
except Exception as e:
    print(f"Warning: Could not import InterviewQuestionGenerator: {e}")

try:
    from src.ml.bias_detector import BiasDetector
    bias_detector = BiasDetector()
except Exception as e:
    print(f"Warning: Could not import BiasDetector: {e}")

try:
    from src.ml.multi_language_support import detect_language_short as ml_support
except Exception as e:
    print(f"Warning: Could not import multi_language_support: {e}")


def analyze_resume(parsed_resume: Dict[str, Any], job_description: Optional[str] = None) -> Dict[str, Any]:
    """Return a canonical dict containing Phase 1 outputs.

    Expected parsed_resume is a dict with at least a 'text' key containing
    the resume raw text or structured fields. This wrapper is defensive and
    will generate warnings if optional modules aren't available.
    """
    out: Dict[str, Any] = {
        'quality': None,
        'skills': None,
        'validated_skills': None,  # ESCO validated skills
        'timeline': None,
        'interview_questions': None,
        'bias_flags': None,
        'language': None,
        'warnings': []
    }

    text = None
    if isinstance(parsed_resume, dict):
        text = parsed_resume.get('text') or parsed_resume.get('raw_text') or ''
    else:
        text = str(parsed_resume)

    # Language detection
    try:
        if ml_support:
            out['language'] = ml_support(text)
        else:
            out['language'] = 'unknown'
            out['warnings'].append('multi_language_support.detect_language_short missing')
    except Exception as e:
        out['language'] = 'unknown'
        out['warnings'].append(f'language detection error: {str(e)}')

    # Resume quality
    try:
        if quality_scorer:
            out['quality'] = quality_scorer.score_resume(parsed_resume)
        else:
            out['warnings'].append('resume_quality_scorer missing')
    except Exception as e:
        out['warnings'].append(f'resume quality error: {str(e)}')

    # Skills mapping with ESCO validation
    try:
        if context_skill_extractor:
            # Extract skills list from resume first
            skills_list = []
            if isinstance(parsed_resume.get('skills'), dict):
                skills_list = parsed_resume.get('skills', {}).get('all_skills', [])
            elif isinstance(parsed_resume.get('skills'), list):
                skills_list = parsed_resume.get('skills', [])
            
            # If no skills in resume, try to extract from text using simple pattern
            if not skills_list:
                # Use dynamic skill extractor or simple extraction as fallback
                import re
                # Extract capitalized tech terms as potential skills
                tech_pattern = r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)*|[A-Z]{2,})\b'
                potential_skills = list(set(re.findall(tech_pattern, text)))
                skills_list = potential_skills[:50]  # Limit to top 50
            
            out['skills'] = context_skill_extractor(parsed_resume, skills_list)
            
            # Apply ESCO validation to extracted skills
            if skill_validator and out['skills']:
                try:
                    # Validate the extracted skills
                    validated_resume = skill_validator.validate_resume_skills(
                        {'skills': out['skills']},
                        threshold=0.8
                    )
                    out['validated_skills'] = validated_resume.get('validated_skills')
                except Exception as e:
                    out['warnings'].append(f'ESCO validation error: {str(e)}')
        else:
            out['warnings'].append('context_aware_skill_extractor missing')
    except Exception as e:
        out['warnings'].append(f'skills mapping error: {str(e)}')

    # Timeline analysis
    try:
        if timeline_analyzer:
            # Extract experience list from parsed resume
            experience_list = parsed_resume.get('experience', []) if isinstance(parsed_resume.get('experience'), list) else []
            out['timeline'] = timeline_analyzer.analyze_timeline(experience_list)
        else:
            out['warnings'].append('experience_timeline_analyzer missing')
    except Exception as e:
        out['warnings'].append(f'timeline error: {str(e)}')

    # Interview questions
    try:
        if question_generator:
            # Convert JD string to dict format expected by generator
            job_dict = {'job_description': job_description} if job_description else {}
            out['interview_questions'] = question_generator.generate(parsed_resume, job_dict)
        else:
            out['warnings'].append('interview_question_generator missing')
    except Exception as e:
        out['warnings'].append(f'interview questions error: {str(e)}')

    # Bias detection
    try:
        if bias_detector:
            out['bias_flags'] = bias_detector.scan_text(text)
        else:
            out['warnings'].append('bias_detector missing')
    except Exception as e:
        out['warnings'].append(f'bias detector error: {str(e)}')

    return out


# Small smoke-run when executed directly
if __name__ == '__main__':
    sample = {
        'text': """
        Professional Summary\nExperienced backend engineer with expertise in Python, Django and AWS.\n\nSkills\nPython, Django, PostgreSQL, AWS, Docker\n\nExperience\nCompany A - Senior Software Engineer (2019-2024)\n- Built microservices using Docker and Kubernetes\n        """
    }

    print('Running Phase1 pipeline smoke test...')
    result = analyze_resume(sample, job_description='Looking for a backend engineer with Python, AWS and microservices experience')
    print('\nPipeline output keys:')
    for k in ['language','quality','skills','timeline','interview_questions','bias_flags','warnings']:
        print(f'- {k}:', type(result.get(k)).__name__ if result.get(k) is not None else 'None')
    print('\nWarnings (if any):')
    for w in result.get('warnings', []):
        print('-', w)
