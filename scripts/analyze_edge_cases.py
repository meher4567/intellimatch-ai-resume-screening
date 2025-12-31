"""
Analyze edge cases where company/title detection failed
to identify patterns for improvement
"""
import json
from pathlib import Path
import re

# Load parsed data
with open('data/training/parsed_resumes_all.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 80)
print("ANALYZING EDGE CASES FOR COMPANY/TITLE DETECTION")
print("=" * 80)

# Find resumes with experience but missing company/title
missing_company = []
missing_title = []
unknown_company = []
unknown_title = []

for resume in data:
    exp = resume.get('experience', [])
    if exp:
        for entry in exp:
            company = entry.get('company', '')
            title = entry.get('title', '')
            
            if not company:
                missing_company.append({
                    'file': resume.get('file_name', 'Unknown'),
                    'entry': entry,
                    'text_preview': resume.get('text', '')[:500]
                })
            elif company == 'Unknown Company':
                unknown_company.append({
                    'file': resume.get('file_name', 'Unknown'),
                    'entry': entry,
                    'text_preview': resume.get('text', '')[:800]
                })
            
            if not title:
                missing_title.append({
                    'file': resume.get('file_name', 'Unknown'),
                    'entry': entry,
                    'text_preview': resume.get('text', '')[:500]
                })
            elif title == 'Unknown Position':
                unknown_title.append({
                    'file': resume.get('file_name', 'Unknown'),
                    'entry': entry,
                    'text_preview': resume.get('text', '')[:800]
                })

print(f"\nMissing Company: {len(missing_company)} entries")
print(f"Unknown Company: {len(unknown_company)} entries")
print(f"Missing Title: {len(missing_title)} entries")
print(f"Unknown Title: {len(unknown_title)} entries")

# Analyze patterns in "Unknown Company" cases
print("\n" + "=" * 80)
print("SAMPLE 'UNKNOWN COMPANY' CASES - Looking for patterns")
print("=" * 80)

for case in unknown_company[:10]:
    print(f"\n{'='*60}")
    print(f"File: {case['file']}")
    print(f"Entry: title={case['entry'].get('title')}, dates={case['entry'].get('start_date')}")
    
    # Look for company-like patterns in raw text
    text = case['text_preview']
    
    # Find lines with potential company indicators
    lines = text.split('\n')
    company_indicators = ['inc', 'corp', 'ltd', 'llc', 'company', 'group', 'hospital', 
                          'university', 'college', 'services', 'systems', 'solutions',
                          'institute', 'center', 'foundation']
    
    print("\nPotential company lines:")
    for line in lines[:30]:
        line = line.strip()
        if any(ind in line.lower() for ind in company_indicators) and len(line) < 80:
            print(f"  > {line}")

# Analyze patterns in "Unknown Title" cases
print("\n" + "=" * 80)
print("SAMPLE 'UNKNOWN TITLE' CASES - Looking for patterns")
print("=" * 80)

for case in unknown_title[:10]:
    print(f"\n{'='*60}")
    print(f"File: {case['file']}")
    print(f"Entry: company={case['entry'].get('company')}, dates={case['entry'].get('start_date')}")
    
    # Look for title-like patterns in raw text
    text = case['text_preview']
    
    # Find lines with potential title patterns
    lines = text.split('\n')
    title_words = ['manager', 'director', 'engineer', 'developer', 'analyst', 'specialist',
                   'coordinator', 'supervisor', 'consultant', 'associate', 'assistant',
                   'administrator', 'technician', 'nurse', 'teacher', 'accountant']
    
    print("\nPotential title lines:")
    for line in lines[:30]:
        line = line.strip()
        if any(tw in line.lower() for tw in title_words) and len(line) < 60:
            print(f"  > {line}")

# Find common resume formats that fail
print("\n" + "=" * 80)
print("DETECTING RESUME FORMAT PATTERNS")
print("=" * 80)

# Check for different date formats in failing resumes
date_patterns_found = {}
for case in unknown_company[:50]:
    text = case['text_preview']
    
    # Check various date patterns
    patterns = {
        'MM/YYYY': r'\d{2}/\d{4}',
        'Month YYYY': r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}',
        'YYYY-YYYY': r'\d{4}\s*[-–—]\s*\d{4}',
        'MM/DD/YYYY': r'\d{1,2}/\d{1,2}/\d{4}',
        'Present': r'(?:present|current)',
    }
    
    for name, pat in patterns.items():
        if re.search(pat, text, re.IGNORECASE):
            date_patterns_found[name] = date_patterns_found.get(name, 0) + 1

print("\nDate pattern frequency in failing resumes:")
for pat, count in sorted(date_patterns_found.items(), key=lambda x: -x[1]):
    print(f"  {pat}: {count}")

# Check structure patterns
print("\n" + "=" * 80)
print("DETECTING STRUCTURE PATTERNS IN FAILING RESUMES")
print("=" * 80)

structure_patterns = {
    'Title first, then company': 0,
    'Company first, then title': 0,
    'Date first': 0,
    'Bullet points only': 0,
    'Table format': 0,
    'Pipe separated': 0,
    'City, State format': 0
}

for case in unknown_company[:100]:
    text = case['text_preview']
    lines = [l.strip() for l in text.split('\n') if l.strip()][:20]
    
    # Check patterns
    if any('|' in l for l in lines):
        structure_patterns['Pipe separated'] += 1
    if any(l.startswith('•') or l.startswith('-') for l in lines):
        structure_patterns['Bullet points only'] += 1
    if any(re.search(r'^\d{2}/\d{4}', l) for l in lines):
        structure_patterns['Date first'] += 1
    if any(re.search(r',\s*[A-Z]{2}\s*$', l) for l in lines):
        structure_patterns['City, State format'] += 1

for pat, count in sorted(structure_patterns.items(), key=lambda x: -x[1]):
    if count > 0:
        print(f"  {pat}: {count}")
