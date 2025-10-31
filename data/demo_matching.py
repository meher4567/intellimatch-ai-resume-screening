"""
Resume-Job Matching Demo
Demonstrates complete pipeline: resume parsing → job parsing → skill matching
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from services.resume_parser import ResumeParser
from services.job_parser import JobParser
from services.skill_extractor import SkillExtractor
from sample_jobs import SAMPLE_JOBS


def print_separator(char='─', length=80):
    """Print separator line"""
    print(char * length)


def demo_matching():
    """Demonstrate resume-job matching"""
    
    print("=" * 80)
    print("RESUME-JOB MATCHING DEMONSTRATION")
    print("IntelliMatch AI - Complete Pipeline")
    print("=" * 80)
    print()
    
    # Initialize parsers
    resume_parser = ResumeParser(detect_sections=True, extract_contact=True, extract_name=True)
    job_parser = JobParser()
    skill_extractor = SkillExtractor()
    
    # Parse a sample resume
    print("📄 Step 1: Parsing Resume...")
    print_separator()
    resume_file = 'data/sample_resumes/john_doe_simple.pdf'
    resume_result = resume_parser.parse(resume_file)
    
    if not resume_result['success']:
        print(f"Failed to parse resume: {resume_result.get('error')}")
        return
    
    print(f"✓ Resume parsed: {resume_result.get('name', 'Unknown')}")
    print(f"  Sections: {', '.join(resume_result.get('sections_found', []))}")
    
    # Extract skills from resume
    resume_skills = skill_extractor.extract_skills(resume_result['text'])
    print(f"  Skills found: {len(resume_skills['all_technical'])} technical skills")
    print()
    
    # Parse job description
    print("💼 Step 2: Parsing Job Description...")
    print_separator()
    job_text = SAMPLE_JOBS['senior_software_engineer']
    job = job_parser.parse(job_text)
    
    print(f"✓ Job parsed: {job.title}")
    print(f"  Company: {job.company}")
    print(f"  Location: {job.location}")
    print(f"  Required skills: {len(job.required_skills)}")
    print()
    
    # Extract skills from job
    job_skills = skill_extractor.extract_skills(job_text)
    print(f"  Skills required: {len(job_skills['all_technical'])} technical skills")
    print()
    
    # Match skills
    print("🎯 Step 3: Matching Skills...")
    print_separator()
    match_result = skill_extractor.match_skills(
        resume_skills['all_technical'],
        job_skills['all_technical']
    )
    
    print(f"✓ Match Score: {match_result['match_percentage']}%")
    print(f"  Matched: {match_result['match_count']}/{match_result['total_required']} skills")
    print()
    
    # Show details
    if match_result['matched_skills']:
        print(f"✅ MATCHED SKILLS ({len(match_result['matched_skills'])}):")
        for skill in match_result['matched_skills'][:15]:
            print(f"  • {skill}")
        if len(match_result['matched_skills']) > 15:
            print(f"  ... and {len(match_result['matched_skills']) - 15} more")
        print()
    
    if match_result['missing_skills']:
        print(f"❌ MISSING SKILLS ({len(match_result['missing_skills'])}):")
        for skill in match_result['missing_skills'][:10]:
            print(f"  • {skill}")
        if len(match_result['missing_skills']) > 10:
            print(f"  ... and {len(match_result['missing_skills']) - 10} more")
        print()
    
    if match_result['extra_skills']:
        print(f"➕ ADDITIONAL SKILLS ({len(match_result['extra_skills'])}):")
        for skill in match_result['extra_skills'][:10]:
            print(f"  • {skill}")
        if len(match_result['extra_skills']) > 10:
            print(f"  ... and {len(match_result['extra_skills']) - 10} more")
        print()
    
    # Show skill breakdown
    print("📊 SKILL BREAKDOWN:")
    print()
    print("Resume Skills:")
    print(f"  Programming Languages: {len(resume_skills['programming_languages'])} "
          f"({', '.join(resume_skills['programming_languages'][:5])})")
    print(f"  Frameworks: {len(resume_skills['frameworks'])} "
          f"({', '.join(resume_skills['frameworks'][:5])})")
    print(f"  Cloud/DevOps: {len(resume_skills['cloud_devops'])} "
          f"({', '.join(resume_skills['cloud_devops'][:5])})")
    print(f"  Databases: {len(resume_skills['databases'])} "
          f"({', '.join(resume_skills['databases'][:3])})")
    print()
    
    print("Job Requirements:")
    print(f"  Programming Languages: {len(job_skills['programming_languages'])} "
          f"({', '.join(job_skills['programming_languages'][:5])})")
    print(f"  Frameworks: {len(job_skills['frameworks'])} "
          f"({', '.join(job_skills['frameworks'][:5])})")
    print(f"  Cloud/DevOps: {len(job_skills['cloud_devops'])} "
          f"({', '.join(job_skills['cloud_devops'][:5])})")
    print(f"  Databases: {len(job_skills['databases'])} "
          f"({', '.join(job_skills['databases'][:3])})")
    print()
    
    # Final verdict
    print("=" * 80)
    print("📈 MATCHING VERDICT:")
    print("=" * 80)
    
    score = match_result['match_percentage']
    if score >= 80:
        verdict = "🟢 STRONG MATCH - Highly recommended"
    elif score >= 60:
        verdict = "🟡 GOOD MATCH - Consider for interview"
    elif score >= 40:
        verdict = "🟠 PARTIAL MATCH - May be suitable with training"
    else:
        verdict = "🔴 WEAK MATCH - Significant skill gaps"
    
    print(f"\n{verdict}")
    print(f"Match Score: {score}%")
    print(f"Matched Skills: {match_result['match_count']}/{match_result['total_required']}")
    print()
    
    print("=" * 80)
    print("✅ Demonstration complete!")
    print("=" * 80)


if __name__ == '__main__':
    demo_matching()
