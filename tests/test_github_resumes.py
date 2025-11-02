"""
Test Hybrid Name Extraction on GitHub Sample Resumes
External validation test
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from ml.hybrid_name_extractor import HybridNameExtractor
import pymupdf


def extract_text_from_pdf(pdf_path):
    """Extract text from PDF"""
    try:
        doc = pymupdf.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return ""


def test_github_resumes():
    """Test on GitHub sample resumes"""
    
    print("="*80)
    print("EXTERNAL VALIDATION: GitHub Resume Dataset")
    print("="*80)
    
    extractor = HybridNameExtractor()
    github_dir = "data/sample_resumes/github_dataset"
    
    # Select diverse test resumes
    test_files = [
        "arasgungore_arasgungore-CV_Aras_Gungore_CV.pdf",
        "deedy_Deedy-Resume_deedy_resume-openfont.pdf",
        "posquit0_Awesome-CV_resume.pdf",
        "posquit0_Awesome-CV_cv.pdf",
        "liantze_AltaCV_sample.pdf",
        "zachscrivena_simple-resume-cv_CV.pdf",
        "jankapunkt_latexcv_main.pdf",
        "cmichi_latex-template-collection_cv.pdf",
        "huajh_awesome-latex-cv_awesome-cv.pdf",
        "liweitianux_resume_resume-zh+en.pdf",  # Chinese + English
    ]
    
    print(f"\nTesting {len(test_files)} diverse GitHub resumes\n")
    
    results = []
    
    for i, filename in enumerate(test_files, 1):
        pdf_path = os.path.join(github_dir, filename)
        
        if not os.path.exists(pdf_path):
            print(f"[{i}/{len(test_files)}] ❌ Not found: {filename}")
            continue
        
        print(f"[{i}/{len(test_files)}] Testing: {filename}")
        
        text = extract_text_from_pdf(pdf_path)
        
        if not text:
            print(f"  ❌ Could not extract text")
            results.append({
                'file': filename,
                'name': None,
                'method': 'parse_failed'
            })
            continue
        
        # Show first few lines
        first_lines = '\n'.join(text.split('\n')[:3])
        print(f"  First lines: {first_lines[:100]}...")
        
        # Extract with details
        details = extractor.extract_with_details(text)
        
        print(f"  ✅ Name: {details['name']}")
        print(f"     Method: {details['method']}")
        print(f"     ML: {details['ml_name']} (conf: {details['ml_confidence']:.2f})")
        print(f"     Rules: {details['rule_name']}")
        
        if details['method'] == 'failed':
            print(f"     ⚠️  BOTH METHODS FAILED!")
        
        results.append({
            'file': filename,
            **details
        })
        print()
    
    # Summary
    print("="*80)
    print("📊 GITHUB DATASET RESULTS")
    print("="*80)
    
    total = len(results)
    success = sum(1 for r in results if r['name'] is not None and r.get('method') != 'parse_failed')
    failed = sum(1 for r in results if r['name'] is None or r.get('method') == 'parse_failed')
    
    method_counts = {
        'both_agree': sum(1 for r in results if r.get('method') == 'both_agree'),
        'rules': sum(1 for r in results if r.get('method') == 'rules'),
        'ml': sum(1 for r in results if r.get('method') == 'ml'),
        'failed': sum(1 for r in results if r.get('method') in ['failed', 'parse_failed'])
    }
    
    print(f"\nTotal Resumes: {total}")
    print(f"  ✅ Success: {success} ({success/total*100:.1f}%)")
    print(f"  ❌ Failed: {failed} ({failed/total*100:.1f}%)")
    
    print(f"\nExtraction Method Breakdown:")
    print(f"  🤝 Both Agree: {method_counts['both_agree']} ({method_counts['both_agree']/total*100:.1f}%)")
    print(f"  📏 Rules Only: {method_counts['rules']} ({method_counts['rules']/total*100:.1f}%)")
    print(f"  🤖 ML Only: {method_counts['ml']} ({method_counts['ml']/total*100:.1f}%)")
    print(f"  ❌ Failed: {method_counts['failed']} ({method_counts['failed']/total*100:.1f}%)")
    
    # Average ML confidence for successful extractions
    successful_ml = [r for r in results if r.get('ml_confidence', 0) > 0]
    if successful_ml:
        avg_ml_conf = sum(r['ml_confidence'] for r in successful_ml) / len(successful_ml)
        print(f"\nAverage ML Confidence: {avg_ml_conf:.2f}")
    
    # Show all results
    print(f"\n{'='*80}")
    print("DETAILED RESULTS:")
    print(f"{'='*80}\n")
    
    for r in results:
        status = "✅" if r.get('name') else "❌"
        print(f"{status} {r['file']}")
        print(f"   Name: {r.get('name')}")
        print(f"   Method: {r.get('method')}")
        print()
    
    # Failures
    failures = [r for r in results if r.get('method') in ['failed', 'parse_failed']]
    if failures:
        print(f"\n{'='*80}")
        print(f"❌ FAILURES ({len(failures)} cases)")
        print(f"{'='*80}\n")
        for r in failures:
            print(f"{r['file']}")
            if r.get('method') == 'parse_failed':
                print(f"  Issue: Could not extract text from PDF")
            else:
                print(f"  ML tried: {r.get('ml_name')}")
                print(f"  Rules tried: {r.get('rule_name')}")
            print()
    
    print("="*80)
    print("✅ GITHUB VALIDATION COMPLETE")
    print("="*80)
    
    # Comparison with Overleaf results
    print("\n📊 COMPARISON: Overleaf vs GitHub")
    print("="*80)
    print("Overleaf Templates: 100% success (22/22)")
    print(f"GitHub Dataset:     {success/total*100:.1f}% success ({success}/{total})")
    
    if success/total >= 0.9:
        print("\n✅ EXCELLENT: System generalizes well to external data!")
    elif success/total >= 0.8:
        print("\n✅ GOOD: Minor differences, but system is robust")
    else:
        print("\n⚠️  NEEDS IMPROVEMENT: Significant gap in external validation")
    
    return results


if __name__ == "__main__":
    results = test_github_resumes()
