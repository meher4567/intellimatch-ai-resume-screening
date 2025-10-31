"""
Comprehensive Resume Parser Test - All 454 PDFs
Tests parser with entire dataset and identifies issues
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.resume_parser import ResumeParser
import logging
from collections import defaultdict

# Setup logging
logging.basicConfig(
    level=logging.WARNING,  # Only show warnings and errors
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_all_resumes():
    """Test parser with all 454 PDF resumes"""
    
    parser = ResumeParser()
    
    # Get all PDF files from all subdirectories
    sample_dir = Path(__file__).parent / "sample_resumes"
    pdf_files = list(sample_dir.rglob("*.pdf"))
    
    print(f"\n{'='*80}")
    print(f"COMPREHENSIVE RESUME PARSER TEST - ALL 454 PDFs")
    print(f"{'='*80}")
    print(f"Testing {len(pdf_files)} PDF files...\n")
    
    # Statistics
    stats = {
        'total': len(pdf_files),
        'successful': 0,
        'failed': 0,
        'empty_text': 0,
        'small_text': 0,  # < 100 chars
        'by_folder': defaultdict(lambda: {'success': 0, 'failed': 0, 'empty': 0})
    }
    
    failed_files = []
    empty_files = []
    small_files = []
    
    # Test each file
    for idx, file_path in enumerate(pdf_files, 1):
        if idx % 50 == 0:
            print(f"Progress: {idx}/{len(pdf_files)} files tested...")
        
        result = parser.parse(str(file_path))
        
        # Get folder name
        folder_name = file_path.parent.name
        
        if result['success']:
            text_length = result.get('char_count', 0)
            
            if text_length == 0:
                stats['empty_text'] += 1
                empty_files.append((file_path.name, folder_name))
                stats['by_folder'][folder_name]['empty'] += 1
            elif text_length < 100:
                stats['small_text'] += 1
                small_files.append((file_path.name, folder_name, text_length))
            else:
                stats['successful'] += 1
                stats['by_folder'][folder_name]['success'] += 1
        else:
            stats['failed'] += 1
            failed_files.append((file_path.name, folder_name, result.get('error', 'Unknown error')))
            stats['by_folder'][folder_name]['failed'] += 1
    
    # Print comprehensive results
    print(f"\n{'='*80}")
    print(f"TEST RESULTS SUMMARY")
    print(f"{'='*80}\n")
    
    print(f"Total files tested: {stats['total']}")
    print(f"✓ Successful (good text): {stats['successful']} ({stats['successful']/stats['total']*100:.1f}%)")
    print(f"⚠ Empty text extracted: {stats['empty_text']} ({stats['empty_text']/stats['total']*100:.1f}%)")
    print(f"⚠ Small text (<100 chars): {stats['small_text']} ({stats['small_text']/stats['total']*100:.1f}%)")
    print(f"✗ Failed to parse: {stats['failed']} ({stats['failed']/stats['total']*100:.1f}%)")
    
    # Results by folder
    print(f"\n{'='*80}")
    print(f"RESULTS BY FOLDER")
    print(f"{'='*80}\n")
    
    for folder, counts in sorted(stats['by_folder'].items()):
        total = counts['success'] + counts['failed'] + counts['empty']
        print(f"{folder}:")
        print(f"  ✓ Success: {counts['success']}/{total}")
        if counts['empty'] > 0:
            print(f"  ⚠ Empty: {counts['empty']}/{total}")
        if counts['failed'] > 0:
            print(f"  ✗ Failed: {counts['failed']}/{total}")
        print()
    
    # Show problematic files
    if failed_files:
        print(f"{'='*80}")
        print(f"FAILED FILES ({len(failed_files)})")
        print(f"{'='*80}\n")
        for name, folder, error in failed_files[:10]:  # Show first 10
            print(f"  {name} ({folder})")
            print(f"    Error: {error[:100]}")
        if len(failed_files) > 10:
            print(f"\n  ... and {len(failed_files) - 10} more")
    
    if empty_files:
        print(f"\n{'='*80}")
        print(f"EMPTY TEXT FILES ({len(empty_files)})")
        print(f"{'='*80}\n")
        for name, folder in empty_files[:10]:
            print(f"  {name} ({folder})")
        if len(empty_files) > 10:
            print(f"\n  ... and {len(empty_files) - 10} more")
    
    if small_files:
        print(f"\n{'='*80}")
        print(f"SMALL TEXT FILES (<100 chars) ({len(small_files)})")
        print(f"{'='*80}\n")
        for name, folder, length in small_files[:10]:
            print(f"  {name} ({folder}): {length} chars")
        if len(small_files) > 10:
            print(f"\n  ... and {len(small_files) - 10} more")
    
    # Success rate calculation
    print(f"\n{'='*80}")
    print(f"FINAL ASSESSMENT")
    print(f"{'='*80}\n")
    
    usable = stats['successful'] + stats['small_text']
    success_rate = (usable / stats['total']) * 100
    
    print(f"Usable extractions: {usable}/{stats['total']} ({success_rate:.1f}%)")
    print(f"Issues to fix: {stats['empty_text'] + stats['failed']} files")
    
    if success_rate >= 95:
        print(f"\n✅ EXCELLENT! Parser is production-ready!")
    elif success_rate >= 85:
        print(f"\n✓ GOOD! Minor improvements needed")
    elif success_rate >= 70:
        print(f"\n⚠ ACCEPTABLE! Significant improvements recommended")
    else:
        print(f"\n✗ NEEDS WORK! Major improvements required")
    
    print(f"\n{'='*80}\n")
    
    return stats, failed_files, empty_files, small_files


if __name__ == "__main__":
    print("\nStarting comprehensive resume parser test...")
    print("This may take 2-3 minutes for 454 PDFs...\n")
    
    stats, failed, empty, small = test_all_resumes()
    
    print("Test complete! Check results above for issues to fix.\n")
