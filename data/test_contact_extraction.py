"""
Contact Information Extraction Test
Test contact extraction across different resume formats
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from services.resume_parser import ResumeParser


def print_separator(char='─', length=80):
    """Print separator line"""
    print(char * length)


def test_contact_extraction():
    """Test contact information extraction"""
    
    print("=" * 80)
    print("CONTACT INFORMATION EXTRACTION TEST")
    print("=" * 80)
    print()
    
    # Initialize parser with contact extraction enabled
    parser = ResumeParser(detect_sections=True, extract_contact=True)
    
    # Test files representing different formats
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
        print(f"  Total text: {result['char_count']:,} chars, {result['word_count']:,} words")
        
        # Display contact information
        contact = result.get('contact_info', {})
        
        if contact:
            print()
            print("📧 CONTACT INFORMATION:")
            
            # Emails
            emails = contact.get('emails', [])
            if emails:
                print(f"  Email(s): {', '.join(emails)}")
            else:
                print("  Email: Not found")
            
            # Phones
            phones = contact.get('phones', [])
            if phones:
                print(f"  Phone(s): {', '.join(phones)}")
            else:
                print("  Phone: Not found")
            
            # LinkedIn
            linkedin = contact.get('linkedin')
            if linkedin:
                print(f"  LinkedIn: {linkedin}")
            else:
                print("  LinkedIn: Not found")
            
            # GitHub
            github = contact.get('github')
            if github:
                print(f"  GitHub: {github}")
            else:
                print("  GitHub: Not found")
            
            # Website
            website = contact.get('website')
            if website:
                print(f"  Website: {website}")
            else:
                print("  Website: Not found")
            
            # Location
            location = contact.get('location')
            if location:
                print(f"  Location: {location}")
            else:
                print("  Location: Not found")
        else:
            print()
            print("  ⚠ No contact information extracted")
        
        print()
    
    print("=" * 80)
    print("Contact extraction test complete!")
    print("=" * 80)


if __name__ == '__main__':
    test_contact_extraction()
