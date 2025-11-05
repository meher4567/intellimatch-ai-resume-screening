"""
Step 2: Extract skills and build comprehensive skill taxonomy
"""

import json
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime
from tqdm import tqdm

# Configuration
INPUT_FILE = Path("data/training/parsed_resumes_all.json")
OUTPUT_DIR = Path("data/training")


def main():
    """Extract skills and build taxonomy"""
    print("\n" + "="*70)
    print("STEP 2: Building Skill Taxonomy")
    print("="*70)
    
    # Load parsed data
    print(f"\n[*] Loading parsed data from {INPUT_FILE}...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        parsed_data = json.load(f)
    
    print(f"   [OK] Loaded {len(parsed_data)} resumes")
    
    # Extract skills
    print("\n[*] Extracting skills...")
    
    skills_by_category = defaultdict(Counter)
    all_skills = Counter()
    skill_cooccurrence = defaultdict(Counter)
    
    for data in tqdm(parsed_data, desc="   Processing"):
        category = data.get("category", "UNKNOWN")
        
        # Extract skills
        if "skills" in data and "all_skills" in data["skills"]:
            skills = data["skills"]["all_skills"]
            
            # Count by category
            skills_by_category[category].update(skills)
            all_skills.update(skills)
            
            # Track co-occurrence
            for i, skill1 in enumerate(skills):
                for skill2 in skills[i+1:]:
                    pair = tuple(sorted([skill1, skill2]))
                    skill_cooccurrence[skill1][skill2] += 1
    
    # Build taxonomy
    print("\n[*] Building taxonomy...")
    
    taxonomy = {
        "version": "2.0",
        "generated_at": datetime.now().isoformat(),
        "source": f"{len(parsed_data)} real resumes across 24 industries",
        "total_unique_skills": len(all_skills),
        "total_skill_mentions": sum(all_skills.values()),
        "top_skills_global": [
            {"skill": s, "count": c} 
            for s, c in all_skills.most_common(500)
        ],
        "skills_by_industry": {
            cat: [{"skill": s, "count": c} for s, c in skills.most_common(100)]
            for cat, skills in skills_by_category.items()
        }
    }
    
    # Save taxonomy
    output_file = OUTPUT_DIR / "skill_taxonomy_v2.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(taxonomy, f, indent=2, ensure_ascii=False)
    
    print(f"   [OK] Saved to: {output_file}")
    
    # Save co-occurrence data
    cooccurrence_data = {
        skill: dict(related.most_common(20))
        for skill, related in list(skill_cooccurrence.items())[:200]
    }
    
    output_file = OUTPUT_DIR / "skill_cooccurrence.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(cooccurrence_data, f, indent=2, ensure_ascii=False)
    
    print(f"   [OK] Co-occurrence data saved")
    
    # Print summary
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"Unique skills:      {taxonomy['total_unique_skills']}")
    print(f"Total mentions:     {taxonomy['total_skill_mentions']}")
    print(f"Avg per resume:     {taxonomy['total_skill_mentions']/len(parsed_data):.1f}")
    
    print(f"\n[*] Top 15 Skills:")
    for i, item in enumerate(taxonomy['top_skills_global'][:15], 1):
        print(f"   {i:2d}. {item['skill']:35s} - {item['count']:5d} mentions")
    
    print(f"\n[OK] Skill taxonomy complete!")


if __name__ == "__main__":
    main()
