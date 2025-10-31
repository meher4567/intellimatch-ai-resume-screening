"""
Comprehensive Resume Analysis
Test complete parser with all features on full dataset
"""

import sys
from pathlib import Path
from collections import Counter

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from services.resume_parser import ResumeParser


def analyze_dataset():
    """Analyze full dataset with all features"""
    
    print("=" * 80)
    print("COMPREHENSIVE RESUME ANALYSIS")
    print("Analyzing full dataset with section detection & contact extraction")
    print("=" * 80)
    print()
    
    # Initialize parser with all features
    parser = ResumeParser(detect_sections=True, extract_contact=True)
    
    # Find all PDFs
    sample_dir = Path('data/sample_resumes')
    pdf_files = list(sample_dir.rglob('*.pdf'))
    
    print(f"Found {len(pdf_files)} PDF files")
    print()
    
    # Statistics
    total_files = len(pdf_files)
    successful = 0
    failed = 0
    
    # Section statistics
    section_counter = Counter()
    
    # Contact statistics
    emails_found = 0
    phones_found = 0
    linkedin_found = 0
    github_found = 0
    websites_found = 0
    locations_found = 0
    
    print("Processing files...")
    for i, pdf_file in enumerate(pdf_files, 1):
        if i % 50 == 0:
            print(f"  Processed {i}/{total_files}...")
        
        result = parser.parse(str(pdf_file))
        
        if result['success']:
            successful += 1
            
            # Count sections
            sections_found = result.get('sections_found', [])
            for section in sections_found:
                section_counter[section] += 1
            
            # Count contact info
            contact = result.get('contact_info', {})
            if contact:
                if contact.get('emails'):
                    emails_found += 1
                if contact.get('phones'):
                    phones_found += 1
                if contact.get('linkedin'):
                    linkedin_found += 1
                if contact.get('github'):
                    github_found += 1
                if contact.get('website'):
                    websites_found += 1
                if contact.get('location'):
                    locations_found += 1
        else:
            failed += 1
    
    print()
    print("=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    print()
    
    # Overall statistics
    print(f"📊 OVERALL STATISTICS:")
    print(f"  Total files: {total_files}")
    print(f"  Successful: {successful} ({successful/total_files*100:.1f}%)")
    print(f"  Failed: {failed} ({failed/total_files*100:.1f}%)")
    print()
    
    # Section detection statistics
    print(f"📑 SECTION DETECTION:")
    print(f"  Total resumes with sections: {sum(section_counter.values())//len(section_counter) if section_counter else 0}")
    for section, count in section_counter.most_common():
        percentage = count / successful * 100
        print(f"  {section.title():20s}: {count:4d} ({percentage:5.1f}%)")
    print()
    
    # Contact extraction statistics
    print(f"📧 CONTACT INFORMATION:")
    print(f"  Emails found:      {emails_found:4d} ({emails_found/successful*100:5.1f}%)")
    print(f"  Phones found:      {phones_found:4d} ({phones_found/successful*100:5.1f}%)")
    print(f"  LinkedIn found:    {linkedin_found:4d} ({linkedin_found/successful*100:5.1f}%)")
    print(f"  GitHub found:      {github_found:4d} ({github_found/successful*100:5.1f}%)")
    print(f"  Websites found:    {websites_found:4d} ({websites_found/successful*100:5.1f}%)")
    print(f"  Locations found:   {locations_found:4d} ({locations_found/successful*100:5.1f}%)")
    print()
    
    print("=" * 80)
    print("Analysis complete!")
    print("=" * 80)


if __name__ == '__main__':
    analyze_dataset()
