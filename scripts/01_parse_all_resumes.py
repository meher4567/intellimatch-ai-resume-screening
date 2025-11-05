"""
Step 1: Parse all 2,500+ resumes and save to JSON
Simple, no heavy ML imports - just parsing
"""

import os
import json
from pathlib import Path
from tqdm import tqdm
from collections import defaultdict
from datetime import datetime

# Lightweight imports only
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.resume_parser import ResumeParser

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


def main():
    """Parse all resumes and save to JSON"""
    print("\n" + "="*70)
    print("STEP 1: Parsing All Resumes")
    print("="*70)
    
    # Collect files
    print("\n[*] Collecting resume files...")
    resume_files = {}
    total_files = 0
    
    for category in CATEGORIES:
        category_path = DATA_DIR / category
        if not category_path.exists():
            continue
        
        files = list(category_path.glob("**/*.[pP][dD][fF]")) + \
                list(category_path.glob("**/*.[dD][oO][cC]")) + \
                list(category_path.glob("**/*.[dD][oO][cC][xX]"))
        
        resume_files[category] = [str(f) for f in files]
        total_files += len(files)
        print(f"   {category:30s} - {len(files):4d} resumes")
    
    print(f"\n[OK] Found {total_files} resumes across {len(resume_files)} categories")
    
    # Parse all resumes
    print("\n[*] Parsing resumes...")
    parser = ResumeParser()
    
    parsed_data = []
    stats = {
        "total": 0,
        "success": 0,
        "failed": 0,
        "by_category": defaultdict(lambda: {"success": 0, "failed": 0, "errors": []})
    }
    
    for category, files in resume_files.items():
        print(f"\n[*] Processing {category} ({len(files)} files)...")
        
        for file_path in tqdm(files, desc=f"   {category}"):
            stats["total"] += 1
            
            try:
                # Parse resume
                result = parser.parse(file_path)
                
                # Add metadata
                result["category"] = category
                result["file_path_original"] = file_path
                result["parsed_at"] = datetime.now().isoformat()
                
                parsed_data.append(result)
                stats["success"] += 1
                stats["by_category"][category]["success"] += 1
                
            except Exception as e:
                error_msg = str(e)[:100]
                stats["failed"] += 1
                stats["by_category"][category]["failed"] += 1
                stats["by_category"][category]["errors"].append({
                    "file": Path(file_path).name,
                    "error": error_msg
                })
    
    # Save parsed data
    print("\n[*] Saving parsed data...")
    output_file = OUTPUT_DIR / "parsed_resumes_all.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(parsed_data, f, indent=2, ensure_ascii=False)
    
    print(f"   [OK] Saved to: {output_file}")
    print(f"   [OK] File size: {output_file.stat().st_size / 1024 / 1024:.1f} MB")
    
    # Save stats
    stats_file = OUTPUT_DIR / "parsing_stats.json"
    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(dict(stats), f, indent=2, default=str)
    
    print(f"   [OK] Stats saved to: {stats_file}")
    
    # Print summary
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"Total processed:  {stats['total']}")
    print(f"Successful:       {stats['success']} ({stats['success']/stats['total']*100:.1f}%)")
    print(f"Failed:           {stats['failed']} ({stats['failed']/stats['total']*100:.1f}%)")
    
    print(f"\n[OK] Parsing complete! Ready for next step.")


if __name__ == "__main__":
    main()
