"""
Job Parser Test
Test job description parsing functionality
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from services.job_parser import JobParser
from sample_jobs import SAMPLE_JOBS


def print_separator(char='─', length=80):
    """Print separator line"""
    print(char * length)


def test_job_parser():
    """Test job parser with sample job descriptions"""
    
    print("=" * 80)
    print("JOB DESCRIPTION PARSER TEST")
    print("=" * 80)
    print()
    
    parser = JobParser()
    
    for job_name, job_text in SAMPLE_JOBS.items():
        print_separator()
        print(f"Testing: {job_name.replace('_', ' ').title()}")
        print_separator()
        print()
        
        # Parse job
        job = parser.parse(job_text)
        
        # Display results
        print("✓ Parsed successfully")
        print()
        
        # Basic info
        print("📋 BASIC INFORMATION:")
        if job.title:
            print(f"  Title: {job.title}")
        if job.company:
            print(f"  Company: {job.company}")
        if job.location:
            print(f"  Location: {job.location}")
        if job.job_type:
            print(f"  Type: {job.job_type}")
        if job.experience_required:
            print(f"  Experience: {job.experience_required}")
        if job.education_required:
            print(f"  Education: {job.education_required}")
        if job.salary_range:
            print(f"  Salary: {job.salary_range}")
        print()
        
        # Responsibilities
        if job.responsibilities:
            print(f"💼 RESPONSIBILITIES ({len(job.responsibilities)}):")
            for i, resp in enumerate(job.responsibilities[:5], 1):
                preview = resp[:100] + '...' if len(resp) > 100 else resp
                print(f"  {i}. {preview}")
            if len(job.responsibilities) > 5:
                print(f"  ... and {len(job.responsibilities) - 5} more")
            print()
        
        # Required Skills/Qualifications
        if job.required_skills:
            print(f"✅ REQUIRED SKILLS/QUALIFICATIONS ({len(job.required_skills)}):")
            for i, skill in enumerate(job.required_skills[:8], 1):
                preview = skill[:100] + '...' if len(skill) > 100 else skill
                print(f"  {i}. {preview}")
            if len(job.required_skills) > 8:
                print(f"  ... and {len(job.required_skills) - 8} more")
            print()
        
        # Preferred Skills
        if job.preferred_skills:
            print(f"⭐ PREFERRED SKILLS ({len(job.preferred_skills)}):")
            for i, skill in enumerate(job.preferred_skills[:5], 1):
                preview = skill[:100] + '...' if len(skill) > 100 else skill
                print(f"  {i}. {preview}")
            print()
        
        # Benefits
        if job.benefits:
            print(f"🎁 BENEFITS ({len(job.benefits)}):")
            for i, benefit in enumerate(job.benefits[:5], 1):
                preview = benefit[:100] + '...' if len(benefit) > 100 else benefit
                print(f"  {i}. {preview}")
            print()
        
        print()
    
    print("=" * 80)
    print("Job parser test complete!")
    print("=" * 80)


if __name__ == '__main__':
    test_job_parser()
