"""
Quick test of the two problem resumes to verify the fix
"""

from src.services.resume_parser import ResumeParser

print("="*80)
print("TESTING FIXES FOR EMPTY EXPERIENCE SECTIONS")
print("="*80)

parser = ResumeParser()

problem_resumes = [
    ('extension-of-debarghya-das-by-alex-sullivan.pdf', 'Alexander Sullivan'),
    ('manisha-singh.pdf', 'Manisha Singh')
]

for filename, expected_name in problem_resumes:
    path = f'data/sample_resumes/overleaf_templates/{filename}'
    
    print(f"\n{'-'*80}")
    print(f"Testing: {filename}")
    print('-'*80)
    
    result = parser.parse(path)
    
    name = result.get('name')
    sections = result.get('sections', {})
    exp_section = sections.get('experience')
    
    print(f"Name: {name} {'[OK]' if name == expected_name else '[MISMATCH]'}")
    
    if exp_section:
        content_len = len(exp_section.get('content', ''))
        print(f"Experience section: FOUND")
        print(f"Content length: {content_len} chars")
        
        if content_len > 0:
            print("Status: FIXED! Content extracted successfully")
            # Show first 200 chars
            content = exp_section.get('content', '')
            preview = content[:200].replace('\n', ' ')
            print(f"Preview: {preview}...")
        else:
            print("Status: STILL EMPTY - FIX FAILED")
    else:
        print("Experience section: NOT FOUND")

print("\n"+"="*80)
print("TEST COMPLETE")
print("="*80)
