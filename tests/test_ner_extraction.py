"""
Test NER Extractor on Overleaf Resumes
Compare ML-based extraction with ground truth
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ml.ner_extractor import NERExtractor, get_best_name_from_entities
from services.name_extractor import NameExtractor
import pymupdf


def extract_text_from_pdf(pdf_path):
    """Extract text from PDF"""
    doc = pymupdf.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def test_ner_name_extraction():
    """Test NER-based name extraction on Overleaf resumes"""
    
    print("="*80)
    print("TESTING ML-BASED NER NAME EXTRACTION")
    print("="*80)
    
    # Initialize extractors
    print("\n🔧 Initializing extractors...")
    ner_extractor = NERExtractor()
    rule_based_extractor = NameExtractor()
    
    # Test resumes directory
    overleaf_dir = "data/sample_resumes/overleaf_templates"
    
    # Get 5 test resumes for initial testing
    test_resumes = [
        "akhil-kollas-resume.pdf",
        "ali-ozens-resume.pdf",
        "aryan-sharmas-cv.pdf",
        "single-page-resume.pdf",
        "vinayak-goels-resume.pdf"
    ]
    
    results = []
    
    for filename in test_resumes:
        pdf_path = os.path.join(overleaf_dir, filename)
        
        if not os.path.exists(pdf_path):
            print(f"\n❌ File not found: {filename}")
            continue
        
        print(f"\n{'='*80}")
        print(f"📄 Testing: {filename}")
        print('='*80)
        
        # Extract text
        text = extract_text_from_pdf(pdf_path)
        print(f"Text length: {len(text)} characters")
        
        # Show first few lines for context
        first_lines = '\n'.join(text.split('\n')[:5])
        print(f"\nFirst lines:\n{first_lines}\n")
        
        # ML-based extraction
        print("🤖 ML-Based NER Extraction:")
        ml_entities = ner_extractor.extract_names(text, top_n=5)
        
        if ml_entities:
            for i, entity in enumerate(ml_entities, 1):
                print(f"  [{i}] {entity.text}")
                print(f"      Confidence: {entity.confidence:.2f}")
                print(f"      Position: chars {entity.start}-{entity.end}")
        else:
            print("  ❌ No names found")
        
        ml_best_name = get_best_name_from_entities(ml_entities)
        print(f"\n  ✅ ML Best Guess: {ml_best_name}")
        
        # Rule-based extraction
        print("\n📏 Rule-Based Extraction:")
        rule_name = rule_based_extractor.extract_name(text)
        print(f"  ✅ Rule-based: {rule_name}")
        
        # Comparison
        print(f"\n🔍 COMPARISON:")
        if ml_best_name and rule_name:
            if ml_best_name.lower() == rule_name.lower():
                print(f"  ✅ MATCH: Both found '{ml_best_name}'")
                status = "MATCH"
            else:
                print(f"  ⚠️  DIFFERENT:")
                print(f"      ML: '{ml_best_name}'")
                print(f"      Rule: '{rule_name}'")
                status = "DIFFERENT"
        elif ml_best_name and not rule_name:
            print(f"  🎯 ML WIN: ML found '{ml_best_name}', Rule-based found nothing")
            status = "ML_WIN"
        elif rule_name and not ml_best_name:
            print(f"  📏 RULE WIN: Rule-based found '{rule_name}', ML found nothing")
            status = "RULE_WIN"
        else:
            print(f"  ❌ BOTH FAILED: Neither found a name")
            status = "BOTH_FAILED"
        
        # Manual verification prompt
        print(f"\n🔍 MANUAL VERIFICATION:")
        print(f"   What is the actual name in this resume?")
        
        results.append({
            'file': filename,
            'ml_name': ml_best_name,
            'rule_name': rule_name,
            'status': status,
            'ml_confidence': ml_entities[0].confidence if ml_entities else 0,
            'ml_candidates': len(ml_entities)
        })
    
    # Summary
    print("\n" + "="*80)
    print("📊 SUMMARY")
    print("="*80)
    
    match_count = sum(1 for r in results if r['status'] == 'MATCH')
    ml_win_count = sum(1 for r in results if r['status'] == 'ML_WIN')
    rule_win_count = sum(1 for r in results if r['status'] == 'RULE_WIN')
    both_failed = sum(1 for r in results if r['status'] == 'BOTH_FAILED')
    different = sum(1 for r in results if r['status'] == 'DIFFERENT')
    
    print(f"\nTotal resumes tested: {len(results)}")
    print(f"  ✅ Match (both agree): {match_count} ({match_count/len(results)*100:.1f}%)")
    print(f"  🎯 ML Win (ML found, rule missed): {ml_win_count}")
    print(f"  📏 Rule Win (rule found, ML missed): {rule_win_count}")
    print(f"  ⚠️  Different (both found different names): {different}")
    print(f"  ❌ Both Failed: {both_failed}")
    
    print(f"\nAverage ML confidence: {sum(r['ml_confidence'] for r in results)/len(results):.2f}")
    
    # Detailed results
    print(f"\n{'='*80}")
    print("DETAILED RESULTS:")
    print(f"{'='*80}")
    for r in results:
        print(f"\n{r['file']}")
        print(f"  ML: {r['ml_name']} (conf: {r['ml_confidence']:.2f}, {r['ml_candidates']} candidates)")
        print(f"  Rule: {r['rule_name']}")
        print(f"  Status: {r['status']}")
    
    print(f"\n{'='*80}")
    print("✅ TEST COMPLETE")
    print(f"{'='*80}")
    print("\nNext steps:")
    print("1. Manually verify which names are correct")
    print("2. Adjust confidence thresholds if needed")
    print("3. Test on more resumes")
    print("4. Integrate ML-based name extraction into parser")


def test_ner_organizations():
    """Test organization extraction"""
    print("\n" + "="*80)
    print("TESTING ORGANIZATION EXTRACTION")
    print("="*80)
    
    ner_extractor = NERExtractor()
    
    # Test on one resume with work experience
    test_file = "single-page-resume.pdf"
    pdf_path = os.path.join("data/sample_resumes/overleaf_templates", test_file)
    
    text = extract_text_from_pdf(pdf_path)
    
    print(f"\nExtracting organizations from: {test_file}\n")
    
    orgs = ner_extractor.extract_organizations(text, min_confidence=0.5)
    
    print(f"Found {len(orgs)} organizations:\n")
    for i, org in enumerate(orgs, 1):
        print(f"  [{i}] {org.text}")
        print(f"      Confidence: {org.confidence:.2f}")
        print(f"      Position: chars {org.start}-{org.end}")
        print()


if __name__ == "__main__":
    # Test name extraction first
    test_ner_name_extraction()
    
    # Then test organizations
    test_ner_organizations()
