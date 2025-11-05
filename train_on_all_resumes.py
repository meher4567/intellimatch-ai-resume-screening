"""
Training Pipeline: Process all 2,500+ resumes across 24 industries
Improves parsing, skill extraction, and classification models
"""

import os
import json
from pathlib import Path
from tqdm import tqdm
import pandas as pd
from collections import defaultdict, Counter
from datetime import datetime

from src.services.resume_parser import ResumeParser
# Skip heavy ML imports for now - just need parser

# Configuration
DATA_DIR = Path("data/data")
OUTPUT_DIR = Path("data/training")
OUTPUT_DIR.mkdir(exist_ok=True)

CATEGORIES = [
    "ACCOUNTANT", "ADVOCATE", "AGRICULTURE", "APPAREL", "ARTS", 
    "AUTOMOBILE", "AVIATION", "BANKING", "BPO", "BUSINESS-DEVELOPMENT",
    "CHEF", "CONSTRUCTION", "CONSULTANT", "DESIGNER", "DIGITAL-MEDIA",
    "ENGINEERING", "FINANCE", "FITNESS", "HEALTHCARE", "HR",
    "INFORMATION-TECHNOLOGY", "PUBLIC-RELATIONS", "SALES", "TEACHER"
]


def collect_all_resumes():
    """Collect all resume file paths by category"""
    print("\n[*] Collecting resume files...")
    
    resume_files = defaultdict(list)
    total = 0
    
    for category in CATEGORIES:
        category_path = DATA_DIR / category
        if not category_path.exists():
            print(f"⚠️  Category not found: {category}")
            continue
        
        files = list(category_path.glob("**/*.[pP][dD][fF]")) + \
                list(category_path.glob("**/*.[dD][oO][cC]")) + \
                list(category_path.glob("**/*.[dD][oO][cC][xX]"))
        
        resume_files[category] = files
        total += len(files)
        print(f"   {category:30s} - {len(files):4d} resumes")
    
    print(f"\n[OK] Total: {total} resumes across {len(CATEGORIES)} categories")
    return resume_files


def parse_all_resumes(resume_files, limit_per_category=None):
    """Parse all resumes and extract structured data"""
    print("\n[*] Parsing all resumes...")
    
    parser = ResumeParser()
    parsed_data = []
    stats = {
        "total": 0,
        "success": 0,
        "failed": 0,
        "by_category": defaultdict(lambda: {"success": 0, "failed": 0})
    }
    
    for category, files in resume_files.items():
        print(f"\n[*] Processing {category}...")
        
        # Limit files if specified (for testing)
        if limit_per_category:
            files = files[:limit_per_category]
        
        for file_path in tqdm(files, desc=f"   {category}"):
            stats["total"] += 1
            
            try:
                # Parse resume
                result = parser.parse(str(file_path))
                
                # Add metadata
                result["category"] = category
                result["file_path_original"] = str(file_path)
                result["parsed_at"] = datetime.now().isoformat()
                
                parsed_data.append(result)
                stats["success"] += 1
                stats["by_category"][category]["success"] += 1
                
            except Exception as e:
                stats["failed"] += 1
                stats["by_category"][category]["failed"] += 1
                print(f"\n   [FAIL] {file_path.name} - {str(e)[:50]}")
    
    return parsed_data, stats


def extract_training_features(parsed_data):
    """Extract features for training ML models"""
    print("\n[*] Extracting training features...")
    
    features = {
        "skills_by_category": defaultdict(Counter),
        "sections_by_category": defaultdict(Counter),
        "organizations_by_category": defaultdict(Counter),
        "all_skills": Counter(),
        "all_sections": Counter(),
        "quality_stats": defaultdict(list),
        "skill_cooccurrence": defaultdict(Counter),
    }
    
    for data in tqdm(parsed_data, desc="   Extracting"):
        category = data.get("category", "UNKNOWN")
        
        # Skills
        if "skills" in data and "all_skills" in data["skills"]:
            skills = data["skills"]["all_skills"]
            features["skills_by_category"][category].update(skills)
            features["all_skills"].update(skills)
            
            # Skill co-occurrence (for better matching)
            for i, skill1 in enumerate(skills):
                for skill2 in skills[i+1:]:
                    pair = tuple(sorted([skill1, skill2]))
                    features["skill_cooccurrence"][skill1][skill2] += 1
        
        # Sections
        if "sections_found" in data:
            sections = data["sections_found"]
            features["sections_by_category"][category].update(sections)
            features["all_sections"].update(sections)
        
        # Organizations
        if "organizations" in data and "all" in data["organizations"]:
            orgs = data["organizations"]["all"]
            features["organizations_by_category"][category].update(orgs)
        
        # Quality scores
        if "quality" in data:
            quality = data["quality"]
            features["quality_stats"][category].append({
                "overall_score": quality.get("overall_score", 0),
                "completeness": quality.get("completeness", 0),
                "readability": quality.get("readability", 0),
            })
    
    return features


def build_skill_taxonomy(features):
    """Build comprehensive skill taxonomy from all resumes"""
    print("\n[*] Building skill taxonomy...")
    
    # Get top skills overall
    top_skills = features["all_skills"].most_common(500)
    
    # Get category-specific skills
    category_skills = {}
    for category, skills in features["skills_by_category"].items():
        category_skills[category] = skills.most_common(50)
    
    taxonomy = {
        "version": "2.0",
        "generated_at": datetime.now().isoformat(),
        "source": "2500+ real resumes across 24 industries",
        "top_skills_global": [{"skill": s, "count": c} for s, c in top_skills],
        "skills_by_industry": {
            cat: [{"skill": s, "count": c} for s, c in skills]
            for cat, skills in category_skills.items()
        },
        "total_unique_skills": len(features["all_skills"]),
        "total_skill_mentions": sum(features["all_skills"].values())
    }
    
    # Save taxonomy
    output_file = OUTPUT_DIR / "skill_taxonomy_v2.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(taxonomy, f, indent=2, ensure_ascii=False)
    
    print(f"   [OK] Saved to: {output_file}")
    print(f"   [OK] {taxonomy['total_unique_skills']} unique skills found")
    
    return taxonomy


def save_training_data(parsed_data, features, stats):
    """Save all training data for future use"""
    print("\n[*] Saving training data...")
    
    # Save parsed resumes
    output_file = OUTPUT_DIR / "parsed_resumes_all.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(parsed_data, f, indent=2, ensure_ascii=False)
    print(f"   [OK] Parsed data: {output_file}")
    
    # Save features
    features_serializable = {
        "skills_by_category": {k: dict(v) for k, v in features["skills_by_category"].items()},
        "sections_by_category": {k: dict(v) for k, v in features["sections_by_category"].items()},
        "organizations_by_category": {k: dict(v) for k, v in features["organizations_by_category"].items()},
        "all_skills": dict(features["all_skills"]),
        "all_sections": dict(features["all_sections"]),
        "quality_stats": dict(features["quality_stats"]),
    }
    
    output_file = OUTPUT_DIR / "training_features.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(features_serializable, f, indent=2, ensure_ascii=False)
    print(f"   [OK] Features: {output_file}")
    
    # Save stats
    output_file = OUTPUT_DIR / "training_stats.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, default=str)
    print(f"   [OK] Stats: {output_file}")
    
    # Create summary CSV
    summary = []
    for category, cat_stats in stats["by_category"].items():
        summary.append({
            "category": category,
            "success": cat_stats["success"],
            "failed": cat_stats["failed"],
            "success_rate": f"{cat_stats['success'] / (cat_stats['success'] + cat_stats['failed']) * 100:.1f}%"
        })
    
    df = pd.DataFrame(summary)
    output_file = OUTPUT_DIR / "training_summary.csv"
    df.to_csv(output_file, index=False)
    print(f"   [OK] Summary: {output_file}")


def print_statistics(stats, features, taxonomy):
    """Print comprehensive training statistics"""
    print("\n" + "="*70)
    print("TRAINING RESULTS")
    print("="*70)
    
    print(f"\n[*] Resume Processing:")
    print(f"   Total processed:     {stats['total']}")
    print(f"   Successful:          {stats['success']} ({stats['success']/stats['total']*100:.1f}%)")
    print(f"   Failed:              {stats['failed']} ({stats['failed']/stats['total']*100:.1f}%)")
    
    print(f"\n[*] Skills Extracted:")
    print(f"   Unique skills:       {taxonomy['total_unique_skills']}")
    print(f"   Total mentions:      {taxonomy['total_skill_mentions']}")
    print(f"   Avg per resume:      {taxonomy['total_skill_mentions']/stats['success']:.1f}")
    
    print(f"\n[*] Top 10 Skills Overall:")
    for i, item in enumerate(taxonomy['top_skills_global'][:10], 1):
        print(f"   {i:2d}. {item['skill']:30s} - {item['count']:4d} mentions")
    
    print(f"\n[*] Sections Found:")
    for section, count in features["all_sections"].most_common(10):
        print(f"   {section:30s} - {count:4d} resumes")
    
    print(f"\n[*] Best Performing Categories:")
    top_categories = sorted(
        stats["by_category"].items(),
        key=lambda x: x[1]["success"],
        reverse=True
    )[:5]
    for category, cat_stats in top_categories:
        success_rate = cat_stats["success"] / (cat_stats["success"] + cat_stats["failed"]) * 100
        print(f"   {category:30s} - {cat_stats['success']:3d} resumes ({success_rate:.1f}%)")
    
    print("\n" + "="*70)


def main():
    """Main training pipeline"""
    print("\n" + "="*70)
    print("TRAINING PIPELINE: Processing 2,500+ Resumes")
    print("="*70)
    
    # Step 1: Collect files
    resume_files = collect_all_resumes()
    
    # Step 2: Parse all resumes
    # Set limit_per_category=10 for quick test, None for full training
    parsed_data, stats = parse_all_resumes(resume_files, limit_per_category=None)
    
    if not parsed_data:
        print("\n[ERROR] No resumes were successfully parsed!")
        return
    
    # Step 3: Extract features
    features = extract_training_features(parsed_data)
    
    # Step 4: Build skill taxonomy
    taxonomy = build_skill_taxonomy(features)
    
    # Step 5: Save everything
    save_training_data(parsed_data, features, stats)
    
    # Step 6: Print results
    print_statistics(stats, features, taxonomy)
    
    print(f"\n[OK] Training complete! Data saved to: {OUTPUT_DIR}")
    print(f"   Use this data to improve matching, classification, and recommendations.")


if __name__ == "__main__":
    main()
