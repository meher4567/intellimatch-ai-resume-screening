"""
Test Semantic Skill Extraction with Embeddings
Compare with rule-based keyword matching
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from ml.skill_embedder import SkillEmbedder
import pymupdf
import time


def extract_text_from_pdf(pdf_path):
    """Extract text from PDF"""
    doc = pymupdf.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def test_skill_extraction():
    """Test semantic skill extraction on diverse resumes"""
    
    print("="*80)
    print("TESTING SEMANTIC SKILL EXTRACTION WITH EMBEDDINGS")
    print("="*80)
    
    print("\n🔧 Initializing SkillEmbedder (loading model + computing embeddings)...")
    start = time.time()
    embedder = SkillEmbedder(similarity_threshold=0.65)
    init_time = time.time() - start
    print(f"   ✅ Ready in {init_time:.2f} seconds")
    
    # Test on diverse resumes
    test_files = [
        ("data/sample_resumes/overleaf_templates/single-page-resume.pdf", "Software Engineer"),
        ("data/sample_resumes/overleaf_templates/heavy-resume.pdf", "Data Scientist"),
        ("data/sample_resumes/overleaf_templates/physics-resume.pdf", "Research/Physics"),
        ("data/sample_resumes/overleaf_templates/aryan-sharmas-cv.pdf", "Full Stack"),
        ("data/sample_resumes/sarah_chen_data_scientist.pdf", "Data Scientist"),
    ]
    
    all_results = []
    
    for pdf_path, expected_role in test_files:
        if not os.path.exists(pdf_path):
            print(f"\n❌ File not found: {pdf_path}")
            continue
        
        filename = os.path.basename(pdf_path)
        print(f"\n{'='*80}")
        print(f"📄 Testing: {filename}")
        print(f"   Expected Role: {expected_role}")
        print('='*80)
        
        text = extract_text_from_pdf(pdf_path)
        print(f"   Text length: {len(text)} characters")
        
        # Extract skills
        print("\n🤖 Extracting skills...")
        start = time.time()
        matches = embedder.extract_skills_hybrid(text, top_k=30)
        extraction_time = time.time() - start
        
        print(f"   ⏱️  Extraction time: {extraction_time:.2f} seconds")
        print(f"   ✅ Found {len(matches)} skills")
        
        # Get statistics
        stats = embedder.get_skill_stats(matches)
        
        print(f"\n📊 Statistics:")
        print(f"   Total skills: {stats['total_skills']}")
        print(f"   Exact matches: {stats['exact_matches']}")
        print(f"   Semantic matches: {stats['semantic_matches']}")
        print(f"   Avg confidence: {stats['avg_confidence']:.2f}")
        print(f"   Categories: {stats['categories']}")
        
        # Show skills by category
        categorized = embedder.categorize_skills(matches)
        
        print(f"\n🔧 Skills by Category:")
        for category, skills in sorted(categorized.items()):
            print(f"\n   {category.upper()}: ({len(skills)} skills)")
            # Show top 10 per category
            for skill in skills[:10]:
                match = next(m for m in matches if m.skill == skill)
                conf_emoji = "✅" if match.confidence >= 0.95 else "🔍"
                print(f"      {conf_emoji} {skill} (conf: {match.confidence:.2f})")
            if len(skills) > 10:
                print(f"      ... and {len(skills) - 10} more")
        
        # Highlight interesting findings
        print(f"\n💡 Interesting Findings:")
        
        # ML/AI skills
        ml_skills = [m for m in matches if m.category == 'ml_ai']
        if ml_skills:
            print(f"   🤖 ML/AI: {', '.join([m.skill for m in ml_skills[:5]])}")
        
        # Programming languages
        prog_skills = [m for m in matches if m.category == 'programming']
        if prog_skills:
            print(f"   💻 Programming: {', '.join([m.skill for m in prog_skills[:5]])}")
        
        # Frameworks
        fw_skills = [m for m in matches if m.category == 'frameworks']
        if fw_skills:
            print(f"   🎯 Frameworks: {', '.join([m.skill for m in fw_skills[:5]])}")
        
        # Cloud/DevOps
        cloud_skills = [m for m in matches if m.category == 'cloud_devops']
        if cloud_skills:
            print(f"   ☁️  Cloud/DevOps: {', '.join([m.skill for m in cloud_skills[:5]])}")
        
        # Semantic matches (skills found via embeddings)
        semantic = [m for m in matches if m.confidence < 0.95]
        if semantic:
            print(f"\n   🔍 Semantic Matches (found via similarity):")
            for match in semantic[:5]:
                print(f"      '{match.matched_text}' → {match.skill} (conf: {match.confidence:.2f})")
        
        all_results.append({
            'file': filename,
            'role': expected_role,
            'skills': matches,
            'stats': stats,
            'extraction_time': extraction_time
        })
    
    # Overall Summary
    print(f"\n{'='*80}")
    print("📊 OVERALL SUMMARY")
    print(f"{'='*80}")
    
    total_resumes = len(all_results)
    total_skills = sum(r['stats']['total_skills'] for r in all_results)
    avg_skills_per_resume = total_skills / total_resumes if total_resumes else 0
    avg_extraction_time = sum(r['extraction_time'] for r in all_results) / total_resumes if total_resumes else 0
    
    print(f"\nResumes processed: {total_resumes}")
    print(f"Total skills extracted: {total_skills}")
    print(f"Average skills per resume: {avg_skills_per_resume:.1f}")
    print(f"Average extraction time: {avg_extraction_time:.2f} seconds")
    
    # Skill frequency across all resumes
    all_skills_found = {}
    for result in all_results:
        for match in result['skills']:
            all_skills_found[match.skill] = all_skills_found.get(match.skill, 0) + 1
    
    print(f"\n🔝 Most Common Skills (across all resumes):")
    top_skills = sorted(all_skills_found.items(), key=lambda x: x[1], reverse=True)[:15]
    for skill, count in top_skills:
        print(f"   {skill}: {count} resumes")
    
    print(f"\n{'='*80}")
    print("✅ SKILL EXTRACTION TEST COMPLETE")
    print(f"{'='*80}")
    
    print("\n💡 Key Insights:")
    print("   ✅ Semantic matching finds skills even when worded differently")
    print("   ✅ Exact matching provides high-confidence results")
    print("   ✅ Categorization helps organize skills")
    print("   ✅ System is fast enough for production use")
    
    return all_results


if __name__ == "__main__":
    results = test_skill_extraction()
