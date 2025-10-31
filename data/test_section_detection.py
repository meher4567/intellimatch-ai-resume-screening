"""
Test Section Detection on Sample Resumes
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.resume_parser import ResumeParser
import logging

logging.basicConfig(level=logging.INFO)


def test_section_detection():
    """Test section detection with real resumes"""
    
    parser = ResumeParser(detect_sections=True)
    
    # Test with a few diverse resumes
    test_files = [
        "sample_resumes/john_doe_simple.pdf",
        "sample_resumes/real_world/my_resume.pdf",
        "sample_resumes/synthetic_dataset/james_chen_data_009.pdf",
        "sample_resumes/overleaf_templates/akhil-kollas-resume.pdf",
        "sample_resumes/github_dataset/posquit0_Awesome-CV_resume.pdf",
    ]
    
    print(f"\n{'='*80}")
    print(f"SECTION DETECTION TEST")
    print(f"{'='*80}\n")
    
    for file_path in test_files:
        full_path = Path(__file__).parent / file_path
        
        if not full_path.exists():
            print(f"⚠ File not found: {file_path}")
            continue
        
        print(f"\n{'─'*80}")
        print(f"Testing: {full_path.name}")
        print(f"{'─'*80}")
        
        result = parser.parse(str(full_path))
        
        if result['success']:
            print(f"✓ Parsed successfully")
            print(f"  Total text: {result['char_count']:,} chars, {result['word_count']:,} words")
            
            if 'sections_found' in result:
                print(f"  Sections detected: {len(result['sections_found'])}")
                
                for section_name in result['sections_found']:
                    section = result['sections'][section_name]
                    print(f"\n  📑 {section_name.upper()}")
                    print(f"     Header: \"{section['raw_header']}\"")
                    print(f"     Content: {section['char_count']:,} chars")
                    print(f"     Confidence: {section['confidence']:.2f}")
                    
                    # Show preview of content
                    preview = section['content'][:150].replace('\n', ' ')
                    print(f"     Preview: {preview}...")
            else:
                print(f"  ⚠ No sections detected")
        else:
            print(f"✗ Failed to parse: {result['error']}")
    
    print(f"\n{'='*80}")
    print(f"Section detection test complete!")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    test_section_detection()
