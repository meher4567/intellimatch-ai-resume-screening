"""
Step 3: Analyze quality patterns and section structures
"""

import json
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime
from tqdm import tqdm
import statistics

# Configuration
INPUT_FILE = Path("data/training/parsed_resumes_all.json")
OUTPUT_DIR = Path("data/training")


def main():
    """Analyze resume quality and structure"""
    print("\n" + "="*70)
    print("STEP 3: Analyzing Quality & Structure")
    print("="*70)
    
    # Load parsed data
    print(f"\n[*] Loading data...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        parsed_data = json.load(f)
    
    print(f"   [OK] Loaded {len(parsed_data)} resumes")
    
    # Analyze
    print("\n[*] Analyzing...")
    
    sections_by_category = defaultdict(Counter)
    all_sections = Counter()
    quality_by_category = defaultdict(list)
    organizations_by_category = defaultdict(Counter)
    
    for data in tqdm(parsed_data, desc="   Processing"):
        category = data.get("category", "UNKNOWN")
        
        # Sections
        if "sections_found" in data:
            sections = data["sections_found"]
            sections_by_category[category].update(sections)
            all_sections.update(sections)
        
        # Quality
        if "quality" in data:
            quality = data["quality"]
            quality_by_category[category].append({
                "overall_score": quality.get("overall_score", 0),
                "completeness": quality.get("completeness", 0),
                "readability": quality.get("readability", 0),
            })
        
        # Organizations
        if "organizations" in data and "all" in data["organizations"]:
            orgs = data["organizations"]["all"]
            organizations_by_category[category].update(orgs)
    
    # Compile analysis
    analysis = {
        "generated_at": datetime.now().isoformat(),
        "total_resumes": len(parsed_data),
        "sections": {
            "all": dict(all_sections),
            "by_category": {
                cat: dict(sections.most_common(20))
                for cat, sections in sections_by_category.items()
            }
        },
        "quality": {
            "by_category": {}
        },
        "top_organizations": dict(Counter(
            {cat: orgs.most_common(1)[0][0] if orgs else None
             for cat, orgs in organizations_by_category.items()}
        ).most_common(50))
    }
    
    # Calculate quality stats
    for category, scores in quality_by_category.items():
        if scores:
            overall = [s["overall_score"] for s in scores]
            analysis["quality"]["by_category"][category] = {
                "avg_score": statistics.mean(overall),
                "median_score": statistics.median(overall),
                "min_score": min(overall),
                "max_score": max(overall),
                "count": len(scores)
            }
    
    # Save analysis
    output_file = OUTPUT_DIR / "resume_analysis.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print(f"\n   [OK] Saved to: {output_file}")
    
    # Print summary
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    
    print(f"\n[*] Most Common Sections:")
    for section, count in all_sections.most_common(10):
        print(f"   {section:30s} - {count:5d} resumes ({count/len(parsed_data)*100:.1f}%)")
    
    print(f"\n[*] Quality Scores by Category (Top 5):")
    top_quality = sorted(
        analysis["quality"]["by_category"].items(),
        key=lambda x: x[1]["avg_score"],
        reverse=True
    )[:5]
    
    for category, stats in top_quality:
        print(f"   {category:30s} - Avg: {stats['avg_score']:.1f}/100")
    
    print(f"\n[OK] Analysis complete!")


if __name__ == "__main__":
    main()
