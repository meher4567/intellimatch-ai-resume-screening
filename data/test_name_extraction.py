"""
Name Extraction Test
Test name extraction across different resume formats
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from services.resume_parser import ResumeParser


def print_separator(char='─', length=80):
    """Print separator line"""
    print(char * length)


def test_name_extraction():
    """Test name extraction"""
    
    print("=" * 80)
    print("NAME EXTRACTION TEST")
    print("=" * 80)
    print()
    
    # Initialize parser with all features
    parser = ResumeParser(detect_sections=True, extract_contact=True, extract_name=True)
    
    # Test files
    test_files = [
        'data/sample_resumes/john_doe_simple.pdf',
        'data/sample_resumes/real_world/my_resume.pdf',
        'data/sample_resumes/synthetic_dataset/james_chen_data_009.pdf',
        'data/sample_resumes/overleaf_templates/akhil-kollas-resume.pdf',
        'data/sample_resumes/github_dataset/posquit0_Awesome-CV_resume.pdf',
    ]
    
    for file_path in test_files:
        print_separator()
        print(f"Testing: {Path(file_path).name}")
        print_separator()
        
        result = parser.parse(file_path)
        
        if not result['success']:
            print(f"✗ Failed to parse: {result.get('error')}")
            print()
            continue
        
        print(f"✓ Parsed successfully")
        
        # Display name
        name = result.get('name')
        if name:
            print(f"  👤 Name: {name}")
        else:
            print(f"  👤 Name: Not found")
        
        # Display first 3 lines of text to verify
        lines = result['text'].split('\n')[:3]
        print()
        print("  First 3 lines:")
        for i, line in enumerate(lines, 1):
            line_preview = line[:70] + '...' if len(line) > 70 else line
            print(f"    {i}. {line_preview}")
        
        print()
    
    print("=" * 80)
    print("Name extraction test complete!")
    print("=" * 80)


if __name__ == '__main__':
    test_name_extraction()
