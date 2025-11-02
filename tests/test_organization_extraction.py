"""
Test Organization Extraction

Tests the OrganizationExtractor on diverse resumes
"""

from pathlib import Path
from src.ml.organization_extractor import OrganizationExtractor


def test_organization_extraction():
    """Test organization extraction on sample resumes"""
    
    print("=" * 80)
    print("TESTING ORGANIZATION/COMPANY EXTRACTION WITH NER")
    print("=" * 80)
    print()
    
    # Initialize extractor
    print("🔧 Initializing OrganizationExtractor...")
    extractor = OrganizationExtractor()
    print("   ✅ Ready")
    print()
    
    # Test resumes with diverse organizations
    test_resumes = [
        "data/sample_resumes/sarah_chen_data_scientist.pdf",
        "data/sample_resumes/overleaf_templates/heavy-resume.pdf",
        "data/sample_resumes/overleaf_templates/aryan-sharmas-cv.pdf",
        "data/sample_resumes/overleaf_templates/single-page-resume.pdf",
        "data/sample_resumes/overleaf_templates/physics-resume.pdf"
    ]
    
    all_results = []
    
    for resume_path in test_resumes:
        if not Path(resume_path).exists():
            print(f"⚠️  Skipping {resume_path} (not found)")
            continue
        
        print("=" * 80)
        print(f"📄 Testing: {Path(resume_path).name}")
        print("=" * 80)
        
        # Read resume text (simple approach)
        from src.services.resume_parser import ResumeParser
        parser = ResumeParser(use_ml=False)  # Don't need ML for text extraction
        result = parser.parse(resume_path)
        
        if not result['success']:
            print(f"   ❌ Failed to parse: {result.get('error')}")
            continue
        
        text = result['text']
        sections = result.get('sections', {})
        
        print(f"   Text length: {len(text)} characters")
        print()
        
        # Extract organizations
        print("🏢 Extracting organizations...")
        orgs = extractor.extract_organizations(text, sections)
        
        print(f"   ✅ Found {len(orgs)} organizations")
        print()
        
        if orgs:
            # Show all organizations
            print("   📋 All Organizations:")
            for org in orgs:
                emoji = "🏢" if org.category == 'company' else "🎓" if org.category == 'university' else "🏛️"
                print(f"      {emoji} {org.name}")
                print(f"         Category: {org.category}")
                print(f"         Confidence: {org.confidence:.2f}")
                if org.section:
                    print(f"         Section: {org.section}")
                print(f"         Context: \"{org.context[:80]}...\"")
                print()
            
            # Get summary
            summary = extractor.get_organization_summary(orgs)
            print("   📊 Summary:")
            print(f"      Total: {summary['total']}")
            print(f"      Companies: {summary['companies']}")
            print(f"      Universities: {summary['universities']}")
            print(f"      Institutions: {summary['institutions']}")
            print(f"      Other: {summary['other']}")
            print(f"      Avg Confidence: {summary['avg_confidence']:.2f}")
            print()
            
            # Extract just companies
            companies = extractor.extract_companies(text, sections)
            if companies:
                print("   🏢 Companies Only:")
                for comp in companies:
                    print(f"      • {comp.name} (confidence: {comp.confidence:.2f})")
                print()
            
            # Extract just universities
            universities = extractor.extract_universities(text, sections)
            if universities:
                print("   🎓 Universities Only:")
                for uni in universities:
                    print(f"      • {uni.name} (confidence: {uni.confidence:.2f})")
                print()
            
            all_results.append({
                'file': Path(resume_path).name,
                'total_orgs': len(orgs),
                'companies': len(companies),
                'universities': len(universities),
                'avg_confidence': summary['avg_confidence']
            })
        else:
            print("   ⚠️  No organizations found")
            all_results.append({
                'file': Path(resume_path).name,
                'total_orgs': 0,
                'companies': 0,
                'universities': 0,
                'avg_confidence': 0
            })
        
        print()
    
    # Overall summary
    print("=" * 80)
    print("📊 OVERALL SUMMARY")
    print("=" * 80)
    print()
    
    if all_results:
        print(f"Resumes processed: {len(all_results)}")
        print()
        
        print("📋 Results Table:")
        print(f"{'File':<40} {'Total':<8} {'Companies':<12} {'Universities':<15} {'Avg Conf':<10}")
        print("-" * 85)
        
        total_orgs = 0
        total_companies = 0
        total_universities = 0
        
        for r in all_results:
            print(f"{r['file']:<40} {r['total_orgs']:<8} {r['companies']:<12} "
                  f"{r['universities']:<15} {r['avg_confidence']:.2f}")
            total_orgs += r['total_orgs']
            total_companies += r['companies']
            total_universities += r['universities']
        
        print("-" * 85)
        print(f"{'TOTAL':<40} {total_orgs:<8} {total_companies:<12} {total_universities:<15}")
        print()
        
        avg_orgs = total_orgs / len(all_results)
        print(f"Average organizations per resume: {avg_orgs:.1f}")
        print(f"Total companies found: {total_companies}")
        print(f"Total universities found: {total_universities}")
        print()
        
        print("✅ ORGANIZATION EXTRACTION TEST COMPLETE")
    else:
        print("⚠️  No resumes were processed")
    
    print("=" * 80)


if __name__ == "__main__":
    test_organization_extraction()
