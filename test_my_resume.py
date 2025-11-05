"""
Test skill extraction on my_resume.pdf
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.resume_parser import parse_resume
import json

print("=" * 70)
print("🧪 TESTING SKILL EXTRACTION ON YOUR RESUME")
print("=" * 70)

resume_path = "data/sample_resumes/real_world/my_resume.pdf"

print(f"\n📄 Parsing: {resume_path}")
print("-" * 70)

result = parse_resume(resume_path)

if result['success']:
    print("\n✅ PARSING SUCCESSFUL!")
    print("=" * 70)
    
    # Basic info
    print(f"\n📋 BASIC INFORMATION:")
    print(f"   Name: {result.get('name', 'Not found')}")
    print(f"   Email: {result.get('email', 'Not found')}")
    print(f"   Phone: {result.get('phone', 'Not found')}")
    
    # Skills
    skills_data = result.get('skills', {})
    all_skills = skills_data.get('all_skills', [])
    by_category = skills_data.get('by_category', {})
    
    print(f"\n🎯 SKILLS EXTRACTED: {len(all_skills)} total")
    print("=" * 70)
    
    if all_skills:
        print(f"\n📊 ALL VALIDATED SKILLS ({len(all_skills)}):")
        for i, skill in enumerate(all_skills, 1):
            print(f"   {i:2}. {skill}")
        
        print(f"\n📂 SKILLS BY CATEGORY:")
        print(f"   ✅ Technical: {len(by_category.get('technical', []))}")
        print(f"   ✅ Soft: {len(by_category.get('soft', []))}")
        print(f"   ✅ Tools: {len(by_category.get('tools', []))}")
        print(f"   ✅ Methodologies: {len(by_category.get('methodologies', []))}")
        
        if by_category.get('technical'):
            print(f"\n💻 TECHNICAL SKILLS:")
            for skill in by_category['technical']:
                print(f"      • {skill}")
        
        if by_category.get('soft'):
            print(f"\n🤝 SOFT SKILLS:")
            for skill in by_category['soft']:
                print(f"      • {skill}")
        
        if by_category.get('tools'):
            print(f"\n🔧 TOOLS:")
            for skill in by_category['tools']:
                print(f"      • {skill}")
        
        if by_category.get('methodologies'):
            print(f"\n📐 METHODOLOGIES:")
            for skill in by_category['methodologies']:
                print(f"      • {skill}")
    else:
        print("   ⚠️ No validated skills found")
    
    # Experience
    experience = result.get('experience', [])
    print(f"\n💼 EXPERIENCE: {len(experience)} entries")
    if experience:
        for i, exp in enumerate(experience[:3], 1):
            print(f"\n   {i}. {exp.get('title', 'N/A')} at {exp.get('company', 'N/A')}")
            if exp.get('duration'):
                print(f"      Duration: {exp['duration']}")
    
    # Education
    education = result.get('education', [])
    print(f"\n🎓 EDUCATION: {len(education)} entries")
    if education:
        for i, edu in enumerate(education, 1):
            print(f"   {i}. {edu.get('degree', 'N/A')} in {edu.get('field', 'N/A')}")
            print(f"      {edu.get('institution', 'N/A')}")
    
    # Sections found
    sections = result.get('sections', {})
    print(f"\n📑 SECTIONS DETECTED:")
    for section, content in sections.items():
        if content:
            print(f"   ✅ {section.title()}")
    
    # Summary
    summary = result.get('summary', '')
    if summary:
        print(f"\n📝 SUMMARY:")
        print(f"   {summary[:200]}..." if len(summary) > 200 else f"   {summary}")
    
    print("\n" + "=" * 70)
    print("✅ ANALYSIS COMPLETE!")
    print("=" * 70)
    
    # Save detailed output
    output_file = "my_resume_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Full details saved to: {output_file}")
    
else:
    print(f"\n❌ PARSING FAILED!")
    print(f"   Error: {result.get('error', 'Unknown error')}")

print()
