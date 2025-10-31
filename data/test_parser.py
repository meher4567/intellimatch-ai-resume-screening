"""
Test Resume Parser with Sample Files
Tests the parser with all available resume files
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.resume_parser import ResumeParser
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_resume_parser():
    """Test parser with all sample resumes"""
    
    # Initialize parser
    parser = ResumeParser()
    
    # Get all resume files (now all in data/sample_resumes/)
    sample_dir = Path(__file__).parent / "sample_resumes"
    
    # Find all PDF, DOCX, TXT files
    resume_files = []
    resume_files.extend(sample_dir.glob("*.pdf"))
    resume_files.extend(sample_dir.glob("*.docx"))
    resume_files.extend(sample_dir.glob("*.txt"))
    resume_files.extend(sample_dir.glob("real_world/*.pdf"))
    resume_files.extend(sample_dir.glob("real_world/*.docx"))
    resume_files.extend(sample_dir.glob("real_world/*.txt"))
    
    print(f"\n{'='*80}")
    print(f"TESTING RESUME PARSER")
    print(f"{'='*80}")
    print(f"Found {len(resume_files)} resume files to test\n")
    
    # Test each file
    results = []
    for file_path in sorted(resume_files):
        print(f"\n{'-'*80}")
        print(f"Testing: {file_path.name}")
        print(f"{'-'*80}")
        
        result = parser.parse(str(file_path))
        results.append(result)
        
        # Print results
        print(f"✓ Success: {result['success']}")
        print(f"✓ File Type: {result['file_type']}")
        print(f"✓ File Size: {result['file_size']:,} bytes")
        print(f"✓ Extraction Method: {result['extraction_method']}")
        
        if result['success']:
            print(f"✓ Text Length: {result['char_count']:,} characters")
            print(f"✓ Word Count: {result['word_count']:,} words")
            
            # Show first 300 chars
            preview = result['text'][:300].replace('\n', ' ')
            print(f"\nPreview: {preview}...")
            
            # Show metadata if available
            if result.get('metadata'):
                metadata = result['metadata']
                if 'num_pages' in metadata:
                    print(f"Metadata: {metadata['num_pages']} pages")
        else:
            print(f"✗ Error: {result['error']}")
    
    # Print summary
    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"Total files tested: {len(results)}")
    print(f"✓ Successful: {len(successful)}")
    print(f"✗ Failed: {len(failed)}")
    
    if failed:
        print(f"\nFailed files:")
        for r in failed:
            print(f"  - {r['file_name']}: {r['error']}")
    
    # Statistics
    if successful:
        avg_chars = sum(r['char_count'] for r in successful) / len(successful)
        avg_words = sum(r['word_count'] for r in successful) / len(successful)
        print(f"\nAverage text length: {avg_chars:,.0f} characters")
        print(f"Average word count: {avg_words:,.0f} words")
    
    print(f"\n{'='*80}\n")
    
    return results


if __name__ == "__main__":
    test_resume_parser()
