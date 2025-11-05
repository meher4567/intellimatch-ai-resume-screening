"""
Upload all 2,484 resumes via API
Uses the running backend server to parse resumes
"""

import requests
from pathlib import Path
from tqdm import tqdm
from collections import defaultdict
import json
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000/api/v1/resumes/batch-upload"
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
    """Upload all resumes via API"""
    print("\n" + "="*70)
    print("Uploading 2,484 Resumes via API")
    print("="*70)
    
    # Collect files
    print("\n[*] Collecting resume files...")
    resume_files = {}
    total_files = 0
    
    for category in CATEGORIES:
        category_path = DATA_DIR / category
        if not category_path.exists():
            continue
        
        files = list(category_path.glob("**/*.[pP][dD][fF]"))
        resume_files[category] = files
        total_files += len(files)
        print(f"   {category:30s} - {len(files):4d} resumes")
    
    print(f"\n[OK] Found {total_files} resumes")
    
    # Upload in batches
    print("\n[*] Uploading resumes...")
    BATCH_SIZE = 10
    
    stats = {
        "total": 0,
        "success": 0,
        "failed": 0,
        "by_category": defaultdict(lambda: {"success": 0, "failed": 0, "errors": []})
    }
    
    for category, files in resume_files.items():
        print(f"\n[*] Processing {category} ({len(files)} files)...")
        
        # Process in batches
        for i in tqdm(range(0, len(files), BATCH_SIZE), desc=f"   {category}"):
            batch = files[i:i+BATCH_SIZE]
            
            # Prepare files for upload
            files_data = []
            for file_path in batch:
                try:
                    files_data.append(
                        ('files', (file_path.name, open(file_path, 'rb'), 'application/pdf'))
                    )
                except Exception as e:
                    stats["failed"] += 1
                    stats["by_category"][category]["failed"] += 1
                    stats["by_category"][category]["errors"].append({
                        "file": file_path.name,
                        "error": str(e)[:100]
                    })
                    continue
            
            # Upload batch
            try:
                response = requests.post(API_URL, files=files_data)
                
                # Close files
                for _, file_tuple in files_data:
                    file_tuple[1].close()
                
                if response.status_code == 200:
                    result = response.json()
                    stats["total"] += result.get("total", 0)
                    stats["success"] += result.get("success_count", 0)
                    stats["failed"] += result.get("failed_count", 0)
                    stats["by_category"][category]["success"] += result.get("success_count", 0)
                    stats["by_category"][category]["failed"] += result.get("failed_count", 0)
                    
                    # Track errors
                    for failed_item in result.get("failed", []):
                        stats["by_category"][category]["errors"].append(failed_item)
                else:
                    # Batch failed
                    stats["failed"] += len(batch)
                    stats["by_category"][category]["failed"] += len(batch)
                    
            except Exception as e:
                # Network error
                stats["failed"] += len(batch)
                stats["by_category"][category]["failed"] += len(batch)
                print(f"\n   [ERROR] Batch upload failed: {str(e)[:50]}")
    
    # Save stats
    print("\n[*] Saving statistics...")
    stats_file = OUTPUT_DIR / "api_upload_stats.json"
    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(dict(stats), f, indent=2, default=str)
    
    print(f"   [OK] Stats saved to: {stats_file}")
    
    # Print summary
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"Total processed:  {stats['total']}")
    print(f"Successful:       {stats['success']} ({stats['success']/stats['total']*100:.1f}%)")
    print(f"Failed:           {stats['failed']}")
    
    print(f"\n[*] Top 5 Categories by Success:")
    top_cats = sorted(
        stats["by_category"].items(),
        key=lambda x: x[1]["success"],
        reverse=True
    )[:5]
    
    for category, cat_stats in top_cats:
        print(f"   {category:30s} - {cat_stats['success']:3d} resumes")
    
    print(f"\n[OK] Upload complete! Check database for parsed resumes.")


if __name__ == "__main__":
    main()
