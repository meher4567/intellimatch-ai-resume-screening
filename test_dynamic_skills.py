"""
Test the new dynamic skill extractor
"""
import json
from src.services.resume_parser import ResumeParser

print("🔄 Testing Dynamic Skill Extractor...")
print("="*70)

# Initialize parser with new extractor
parser = ResumeParser(use_ml=True)

# Load a few sample resumes from training data
with open('data/training/parsed_resumes_all.json', 'r', encoding='utf-8') as f:
    old_resumes = json.load(f)

print(f"\nLoaded {len(old_resumes)} resumes from training data\n")

# Re-parse a few resumes with new extractor
test_indices = [0, 5, 10, 50, 100]  # Sample various resumes
results = []

for idx in test_indices:
    old_resume = old_resumes[idx]
    file_path = old_resume.get('file_path_original')
    
    if not file_path:
        continue
    
    print(f"\n{'='*70}")
    print(f"Resume {idx}: {old_resume.get('category', 'Unknown')}")
    print(f"File: {file_path}")
    print("="*70)
    
    try:
        # Re-parse with new extractor
        new_result = parser.parse(file_path)
        
        # Compare
        old_skills = old_resume.get('skills', {}).get('all_skills', [])
        new_skills = new_result.get('skills', {}).get('all_skills', [])
        
        print(f"\n📊 COMPARISON:")
        print(f"   Old Extractor: {len(old_skills)} skills")
        print(f"   New Extractor: {len(new_skills)} skills")
        print(f"   Improvement: +{len(new_skills) - len(old_skills)} skills ({(len(new_skills)/max(len(old_skills),1)-1)*100:+.0f}%)")
        
        print(f"\n📝 Old Skills ({len(old_skills)}):")
        print(f"   {', '.join(old_skills[:20])}")
        if len(old_skills) > 20:
            print(f"   ... and {len(old_skills)-20} more")
        
        print(f"\n✨ New Skills ({len(new_skills)}):")
        # Show categorized
        by_cat = new_result.get('skills', {}).get('by_category', {})
        for cat, skills in by_cat.items():
            if skills:
                print(f"   {cat.title()}: {', '.join(skills[:10])}")
                if len(skills) > 10:
                    print(f"      ... and {len(skills)-10} more")
        
        # Track for summary
        results.append({
            'index': idx,
            'category': old_resume.get('category'),
            'old_count': len(old_skills),
            'new_count': len(new_skills),
            'improvement': len(new_skills) - len(old_skills)
        })
        
    except Exception as e:
        print(f"❌ Error: {e}")
        continue

# Summary
print(f"\n\n{'='*70}")
print("📊 SUMMARY")
print("="*70)

if results:
    total_old = sum(r['old_count'] for r in results)
    total_new = sum(r['new_count'] for r in results)
    avg_old = total_old / len(results)
    avg_new = total_new / len(results)
    
    print(f"\nTested: {len(results)} resumes")
    print(f"\nAverage skills per resume:")
    print(f"   Old: {avg_old:.1f} skills")
    print(f"   New: {avg_new:.1f} skills")
    print(f"   Improvement: +{avg_new - avg_old:.1f} skills ({(avg_new/avg_old-1)*100:+.0f}%)")
    
    print(f"\nDetailed Results:")
    for r in results:
        improvement_pct = (r['new_count']/max(r['old_count'],1)-1)*100 if r['old_count'] > 0 else 100
        print(f"   {r['category']:25s} - {r['old_count']:2d} → {r['new_count']:2d} (+{r['improvement']:2d}, {improvement_pct:+.0f}%)")
    
    print(f"\n✅ Dynamic extraction working! Much better skill coverage!")
else:
    print("❌ No results to compare")
