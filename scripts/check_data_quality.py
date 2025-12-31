"""Check data quality issues"""
import json
from pathlib import Path
from collections import Counter

# Load resumes
with open('data/training/parsed_resumes_all.json', 'r', encoding='utf-8') as f:
    resumes = json.load(f)

print("="*60)
print("DATA QUALITY CHECK")
print("="*60)

# Check experience data
print(f"\nTotal resumes: {len(resumes)}")

has_experience = 0
has_duration = 0
has_title = 0
total_exp_entries = 0

for r in resumes:
    exp = r.get('experience', [])
    if exp:
        has_experience += 1
        total_exp_entries += len(exp)
        for e in exp:
            if e.get('duration_months') is not None:
                has_duration += 1
            if e.get('title'):
                has_title += 1

print(f"\nExperience Data Quality:")
print(f"  Resumes with experience: {has_experience}/{len(resumes)} ({has_experience/len(resumes)*100:.1f}%)")
print(f"  Total experience entries: {total_exp_entries}")
print(f"  Entries with duration_months: {has_duration}/{total_exp_entries} ({has_duration/total_exp_entries*100:.1f}%)" if total_exp_entries else "  No entries")
print(f"  Entries with title: {has_title}/{total_exp_entries} ({has_title/total_exp_entries*100:.1f}%)" if total_exp_entries else "  No entries")

# Check skills data
print(f"\nSkills Data Quality:")
has_skills = 0
skills_as_dict = 0
skills_as_list = 0

for r in resumes:
    skills = r.get('skills')
    if skills:
        has_skills += 1
        if isinstance(skills, dict):
            skills_as_dict += 1
        elif isinstance(skills, list):
            skills_as_list += 1

print(f"  Resumes with skills: {has_skills}/{len(resumes)} ({has_skills/len(resumes)*100:.1f}%)")
print(f"  Skills as dict: {skills_as_dict}")
print(f"  Skills as list: {skills_as_list}")

# Check education data
print(f"\nEducation Data Quality:")
has_education = 0
has_degree = 0

for r in resumes:
    edu = r.get('education', [])
    if edu:
        has_education += 1
        for e in edu:
            if e.get('degree'):
                has_degree += 1

print(f"  Resumes with education: {has_education}/{len(resumes)} ({has_education/len(resumes)*100:.1f}%)")

# Sample a few resumes
print("\n" + "="*60)
print("SAMPLE RESUMES (first 3)")
print("="*60)

for i, r in enumerate(resumes[:3]):
    print(f"\n--- Resume {i+1}: {r.get('name', 'Unknown')[:40]} ---")
    print(f"Skills type: {type(r.get('skills')).__name__}")
    skills = r.get('skills', {})
    if isinstance(skills, dict):
        all_skills = skills.get('all_skills', [])
        print(f"Skills ({len(all_skills)}): {all_skills[:5]}...")
    else:
        print(f"Skills ({len(skills) if skills else 0}): {skills[:5] if skills else 'None'}...")
    
    exp = r.get('experience', [])
    print(f"Experience entries: {len(exp)}")
    for e in exp[:2]:
        print(f"  - {e.get('title', 'No title')[:30]} | {e.get('duration_months')} months")
    
    edu = r.get('education', [])
    print(f"Education entries: {len(edu)}")
    for e in edu[:1]:
        print(f"  - {e.get('degree', 'No degree')} in {e.get('field', 'Unknown field')}")

print("\n" + "="*60)
print("RECOMMENDATIONS")
print("="*60)

issues = []
if has_duration / total_exp_entries < 0.5 if total_exp_entries else True:
    issues.append("❌ Most experience entries missing duration_months - experience scoring unreliable")
if has_education / len(resumes) < 0.5:
    issues.append("❌ Most resumes missing education data")
if has_experience / len(resumes) < 0.8:
    issues.append("⚠️ Many resumes missing experience data")

if issues:
    for issue in issues:
        print(f"  {issue}")
else:
    print("  ✅ Data quality looks good!")
