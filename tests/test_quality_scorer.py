"""
Test Quality Scorer

Tests quality assessment on sample resumes
"""

import os
from pathlib import Path
from src.services.pdf_extractor import extract_text_from_pdf
from src.services.quality_scorer import QualityScorer, assess_quality


def test_quality_scorer():
    """Test quality scorer on sample resumes"""
    
    # Find resume directory
    data_dir = Path("data/sample_resumes")
    if not data_dir.exists():
        print(f"❌ Directory not found: {data_dir}")
        return
    
    # Get some sample PDFs
    pdf_files = list(data_dir.glob("**/*.pdf"))[:10]
    
    if not pdf_files:
        print("❌ No PDF files found")
        return
    
    print(f"Testing Quality Scorer on {len(pdf_files)} resumes...\n")
    print("=" * 80)
    
    scorer = QualityScorer()
    scores_summary = []
    
    for pdf_path in pdf_files:
        print(f"\n📄 {pdf_path.name}")
        print("-" * 80)
        
        try:
            # Extract text
            text = extract_text_from_pdf(str(pdf_path))
            
            # Assess quality
            quality = scorer.assess_quality(str(pdf_path), text)
            
            # Display results
            print(f"\n📊 Quality Scores:")
            print(f"  Overall:     {quality.overall_score:.1f}/100")
            print(f"  Extraction:  {quality.extraction_quality:.1f}/100")
            print(f"  Completeness: {quality.completeness:.1f}/100")
            print(f"  Formatting:  {quality.formatting_quality:.1f}/100")
            print(f"  Readability: {quality.readability:.1f}/100")
            
            print(f"\n📋 Properties:")
            print(f"  Is Scanned: {quality.is_scanned}")
            print(f"  Has Images: {quality.has_images}")
            print(f"  Text Length: {len(text)} chars")
            
            if quality.issues:
                print(f"\n⚠️  Issues ({len(quality.issues)}):")
                for issue in quality.issues[:5]:  # Show first 5
                    print(f"  • {issue}")
            
            if quality.recommendations:
                print(f"\n💡 Recommendations ({len(quality.recommendations)}):")
                for rec in quality.recommendations[:5]:  # Show first 5
                    print(f"  • {rec}")
            
            # Store for summary
            scores_summary.append({
                'name': pdf_path.name,
                'overall': quality.overall_score,
                'extraction': quality.extraction_quality,
                'completeness': quality.completeness,
                'is_scanned': quality.is_scanned
            })
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Overall summary
    print("\n" + "=" * 80)
    print("\n📈 SUMMARY STATISTICS")
    print("=" * 80)
    
    if scores_summary:
        avg_overall = sum(s['overall'] for s in scores_summary) / len(scores_summary)
        avg_extraction = sum(s['extraction'] for s in scores_summary) / len(scores_summary)
        avg_completeness = sum(s['completeness'] for s in scores_summary) / len(scores_summary)
        scanned_count = sum(1 for s in scores_summary if s['is_scanned'])
        
        print(f"\n📊 Average Scores:")
        print(f"  Overall Quality: {avg_overall:.1f}/100")
        print(f"  Extraction Quality: {avg_extraction:.1f}/100")
        print(f"  Completeness: {avg_completeness:.1f}/100")
        
        print(f"\n📋 Document Analysis:")
        print(f"  Total Resumes: {len(scores_summary)}")
        print(f"  Scanned Documents: {scanned_count}")
        print(f"  Native PDFs: {len(scores_summary) - scanned_count}")
        
        # Quality distribution
        high_quality = len([s for s in scores_summary if s['overall'] >= 80])
        medium_quality = len([s for s in scores_summary if 60 <= s['overall'] < 80])
        low_quality = len([s for s in scores_summary if s['overall'] < 60])
        
        print(f"\n🎯 Quality Distribution:")
        print(f"  High Quality (≥80):  {high_quality} ({high_quality/len(scores_summary)*100:.1f}%)")
        print(f"  Medium Quality (60-79): {medium_quality} ({medium_quality/len(scores_summary)*100:.1f}%)")
        print(f"  Low Quality (<60):   {low_quality} ({low_quality/len(scores_summary)*100:.1f}%)")
        
        # Best and worst
        best = max(scores_summary, key=lambda x: x['overall'])
        worst = min(scores_summary, key=lambda x: x['overall'])
        
        print(f"\n🏆 Best Resume:")
        print(f"  {best['name']}: {best['overall']:.1f}/100")
        
        print(f"\n⚠️  Needs Improvement:")
        print(f"  {worst['name']}: {worst['overall']:.1f}/100")


if __name__ == "__main__":
    test_quality_scorer()
