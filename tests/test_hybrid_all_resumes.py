"""
Comprehensive Test: Hybrid Name Extraction on All 22 Overleaf Resumes
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from ml.hybrid_name_extractor import HybridNameExtractor
import pymupdf


def extract_text_from_pdf(pdf_path):
    """Extract text from PDF"""
    doc = pymupdf.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def test_all_resumes():
    """Test hybrid extraction on all 22 Overleaf resumes"""
    
    print("="*80)
    print("COMPREHENSIVE TEST: HYBRID NAME EXTRACTION")
    print("Testing on ALL 22 Overleaf Template Resumes")
    print("="*80)
    
    extractor = HybridNameExtractor()
    overleaf_dir = "data/sample_resumes/overleaf_templates"
    
    # Get all PDFs
    pdf_files = sorted([f for f in os.listdir(overleaf_dir) if f.endswith('.pdf')])
    
    print(f"\nFound {len(pdf_files)} resumes to test\n")
    
    results = []
    
    for i, filename in enumerate(pdf_files, 1):
        pdf_path = os.path.join(overleaf_dir, filename)
        
        print(f"[{i}/{len(pdf_files)}] Testing: {filename}")
        
        text = extract_text_from_pdf(pdf_path)
        
        # Extract with details
        details = extractor.extract_with_details(text)
        
        print(f"  ✅ Final: {details['name']}")
        print(f"     Method: {details['method']}")
        print(f"     ML: {details['ml_name']} (conf: {details['ml_confidence']:.2f})")
        print(f"     Rules: {details['rule_name']}")
        
        if details['method'] == 'failed':
            print(f"     ⚠️  ATTENTION: Both methods failed!")
        
        results.append({
            'file': filename,
            **details
        })
        print()
    
    # Summary Statistics
    print("="*80)
    print("📊 SUMMARY STATISTICS")
    print("="*80)
    
    total = len(results)
    success = sum(1 for r in results if r['name'] is not None)
    failed = sum(1 for r in results if r['name'] is None)
    
    method_counts = {
        'both_agree': sum(1 for r in results if r['method'] == 'both_agree'),
        'rules': sum(1 for r in results if r['method'] == 'rules'),
        'ml': sum(1 for r in results if r['method'] == 'ml'),
        'failed': sum(1 for r in results if r['method'] == 'failed')
    }
    
    print(f"\nTotal Resumes: {total}")
    print(f"  ✅ Success: {success} ({success/total*100:.1f}%)")
    print(f"  ❌ Failed: {failed} ({failed/total*100:.1f}%)")
    
    print(f"\nExtraction Method Breakdown:")
    print(f"  🤝 Both Agree: {method_counts['both_agree']} ({method_counts['both_agree']/total*100:.1f}%)")
    print(f"  📏 Rules Only: {method_counts['rules']} ({method_counts['rules']/total*100:.1f}%)")
    print(f"  🤖 ML Only: {method_counts['ml']} ({method_counts['ml']/total*100:.1f}%)")
    print(f"  ❌ Failed: {method_counts['failed']} ({method_counts['failed']/total*100:.1f}%)")
    
    # Average ML confidence
    avg_ml_conf = sum(r['ml_confidence'] for r in results if r['ml_confidence']) / len([r for r in results if r['ml_confidence']])
    print(f"\nAverage ML Confidence: {avg_ml_conf:.2f}")
    
    # Detailed breakdown
    print(f"\n{'='*80}")
    print("DETAILED RESULTS")
    print(f"{'='*80}\n")
    
    for r in results:
        status = "✅" if r['name'] else "❌"
        print(f"{status} {r['file']}")
        print(f"   Name: {r['name']}")
        print(f"   Method: {r['method']}")
        if r['method'] == 'failed':
            print(f"   ⚠️  ML tried: {r['ml_name']}, Rules tried: {r['rule_name']}")
        print()
    
    # Cases where methods disagreed
    disagreements = [r for r in results if r['ml_name'] and r['rule_name'] and r['ml_name'].lower() != r['rule_name'].lower()]
    if disagreements:
        print(f"\n{'='*80}")
        print(f"⚠️  DISAGREEMENTS ({len(disagreements)} cases)")
        print(f"{'='*80}\n")
        for r in disagreements:
            print(f"{r['file']}")
            print(f"  ML: {r['ml_name']} (conf: {r['ml_confidence']:.2f})")
            print(f"  Rules: {r['rule_name']}")
            print(f"  Final: {r['name']} (used {r['method']})")
            print()
    
    # Failures
    if method_counts['failed'] > 0:
        print(f"\n{'='*80}")
        print(f"❌ FAILURES ({method_counts['failed']} cases)")
        print(f"{'='*80}\n")
        for r in results:
            if r['method'] == 'failed':
                print(f"{r['file']}")
                print(f"  ML candidates: {r['all_ml_candidates']}")
                print()
    
    print("="*80)
    print("✅ TEST COMPLETE")
    print("="*80)
    
    return results


if __name__ == "__main__":
    results = test_all_resumes()
