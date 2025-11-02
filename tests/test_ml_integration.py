"""
Test ML Integration in Resume Parser

Tests the integrated HybridNameExtractor and SkillEmbedder in the main parser
"""

import json
from pathlib import Path
from src.services.resume_parser import ResumeParser


def test_ml_integration():
    """Test ML extractors integrated in main parser"""
    
    print("=" * 80)
    print("TESTING ML INTEGRATION IN RESUME PARSER")
    print("=" * 80)
    print()
    
    # Initialize parser with ML enabled
    print("🔧 Initializing ResumeParser with ML extractors...")
    parser = ResumeParser(use_ml=True)
    print("   ✅ Parser ready (ML enabled)")
    print()
    
    # Test on a few diverse resumes
    test_resumes = [
        "data/sample_resumes/overleaf_templates/single-page-resume.pdf",
        "data/sample_resumes/overleaf_templates/heavy-resume.pdf",
        "data/sample_resumes/overleaf_templates/aryan-sharmas-cv.pdf"
    ]
    
    results = []
    
    for resume_path in test_resumes:
        if not Path(resume_path).exists():
            print(f"⚠️  Skipping {resume_path} (not found)")
            continue
        
        print("=" * 80)
        print(f"📄 Testing: {Path(resume_path).name}")
        print("=" * 80)
        
        # Parse resume
        result = parser.parse(resume_path)
        
        if not result['success']:
            print(f"   ❌ Parsing failed: {result.get('error')}")
            continue
        
        print(f"   ✅ Parsed successfully")
        print(f"   📊 Text length: {len(result['text'])} chars")
        print()
        
        # Check name extraction
        print("👤 Name Extraction:")
        if 'name' in result:
            print(f"   Name: {result['name']}")
            if 'name_extraction' in result:
                ne = result['name_extraction']
                print(f"   Method: {ne['method']}")
                if ne.get('confidence'):
                    print(f"   Confidence: {ne['confidence']:.2f}")
                print(f"   ML Enabled: {ne['ml_enabled']}")
        else:
            print("   ⚠️  No name extracted")
        print()
        
        # Check skill extraction
        print("🎯 Skill Extraction:")
        if 'skills' in result:
            skills = result['skills']
            print(f"   Total skills: {len(skills['all_skills'])}")
            print(f"   Extraction method: {skills.get('extraction_method', 'unknown')}")
            
            if 'stats' in skills:
                stats = skills['stats']
                print(f"   Exact matches: {stats['exact_matches']}")
                print(f"   Semantic matches: {stats['semantic_matches']}")
                print(f"   Avg confidence: {stats['avg_confidence']:.2f}")
                print(f"   Categories: {stats['categories']}")
            
            print()
            print("   📂 Skills by Category:")
            for category, category_skills in skills['by_category'].items():
                if category_skills:
                    print(f"      {category.upper()}: {len(category_skills)} skills")
                    # Show top 5 skills in each category
                    for skill in category_skills[:5]:
                        print(f"         • {skill}")
                    if len(category_skills) > 5:
                        print(f"         ... and {len(category_skills) - 5} more")
        else:
            print("   ⚠️  No skills extracted")
        
        print()
        
        # Check organization extraction
        print("🏢 Organization Extraction:")
        if 'organizations' in result:
            orgs = result['organizations']
            print(f"   Total organizations: {len(orgs['all'])}")
            print(f"   Companies: {len(orgs['companies'])}")
            print(f"   Universities: {len(orgs['universities'])}")
            print(f"   Extraction method: {orgs.get('extraction_method', 'unknown')}")
            
            if orgs['companies']:
                print()
                print("   🏢 Companies:")
                for company in orgs['companies'][:5]:
                    print(f"      • {company}")
                if len(orgs['companies']) > 5:
                    print(f"      ... and {len(orgs['companies']) - 5} more")
            
            if orgs['universities']:
                print()
                print("   🎓 Universities:")
                for uni in orgs['universities'][:5]:
                    print(f"      • {uni}")
                if len(orgs['universities']) > 5:
                    print(f"      ... and {len(orgs['universities']) - 5} more")
        else:
            print("   ⚠️  No organizations extracted")
        
        print()
        
        # Store result
        results.append({
            'file': Path(resume_path).name,
            'name': result.get('name'),
            'name_method': result.get('name_extraction', {}).get('method'),
            'skills_count': len(result.get('skills', {}).get('all_skills', [])),
            'exact_matches': result.get('skills', {}).get('stats', {}).get('exact_matches', 0),
            'semantic_matches': result.get('skills', {}).get('stats', {}).get('semantic_matches', 0),
            'orgs_count': len(result.get('organizations', {}).get('all', [])),
            'companies': len(result.get('organizations', {}).get('companies', [])),
            'universities': len(result.get('organizations', {}).get('universities', [])),
        })
    
    # Summary
    print("=" * 80)
    print("📊 INTEGRATION TEST SUMMARY")
    print("=" * 80)
    print()
    
    if results:
        print(f"Resumes processed: {len(results)}")
        print()
        
        print("📋 Results Table:")
        print(f"{'File':<30} {'Name':<15} {'Skills':<8} {'Exact':<7} {'Sem':<5} {'Orgs':<6} {'Cos':<5} {'Unis':<5}")
        print("-" * 90)
        
        total_skills = 0
        total_exact = 0
        total_semantic = 0
        total_orgs = 0
        total_companies = 0
        total_unis = 0
        
        for r in results:
            print(f"{r['file']:<30} {(r['name'] or 'N/A'):<15} "
                  f"{r['skills_count']:<8} {r['exact_matches']:<7} {r['semantic_matches']:<5} "
                  f"{r['orgs_count']:<6} {r['companies']:<5} {r['universities']:<5}")
            total_skills += r['skills_count']
            total_exact += r['exact_matches']
            total_semantic += r['semantic_matches']
            total_orgs += r['orgs_count']
            total_companies += r['companies']
            total_unis += r['universities']
        
        print("-" * 90)
        print(f"{'TOTAL':<30} {'':<15} {total_skills:<8} {total_exact:<7} {total_semantic:<5} "
              f"{total_orgs:<6} {total_companies:<5} {total_unis:<5}")
        print()
        
        avg_skills = total_skills / len(results)
        avg_orgs = total_orgs / len(results)
        semantic_pct = (total_semantic / total_skills * 100) if total_skills > 0 else 0
        
        print(f"Average skills per resume: {avg_skills:.1f}")
        print(f"Average organizations per resume: {avg_orgs:.1f}")
        print(f"Semantic matches: {semantic_pct:.1f}% of total skills")
        print(f"Total companies found: {total_companies}")
        print(f"Total universities found: {total_unis}")
        print()
        
        print("✅ ML INTEGRATION TEST COMPLETE")
    else:
        print("⚠️  No resumes were processed")
    
    print("=" * 80)


if __name__ == "__main__":
    test_ml_integration()
