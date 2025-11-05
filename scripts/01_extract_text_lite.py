"""
Step 1 LITE: Quick parse using only basic text extraction
No ML models loaded - just extract text and basic info
"""

import os
import json
from pathlib import Path
from tqdm import tqdm
from collections import defaultdict
from datetime import datetime
import PyPDF2
import docx

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


def extract_text_pdf(file_path):
    """Extract text from PDF"""
    try:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except:
        return ""


def extract_text_docx(file_path):
    """Extract text from DOCX"""
    try:
        doc = docx.Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except:
        return ""


def extract_text(file_path):
    """Extract text from any supported format"""
    ext = Path(file_path).suffix.lower()
    
    if ext == '.pdf':
        return extract_text_pdf(file_path)
    elif ext in ['.docx', '.doc']:
        return extract_text_docx(file_path)
    else:
        return ""


def main():
    """Quick parse - text extraction only"""
    print("\n" + "="*70)
    print("STEP 1 LITE: Quick Text Extraction (No ML)")
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
    
    print(f"\n[OK] Found {total_files} resumes")
    
    # Extract text from all resumes
    print("\n[*] Extracting text...")
    
    extracted_data = []
    stats = {
        "total": 0,
        "success": 0,
        "failed": 0,
        "by_category": defaultdict(lambda: {"success": 0, "failed": 0})
    }
    
    for category, files in resume_files.items():
        print(f"\n[*] Processing {category} ({len(files)} files)...")
        
        for file_path in tqdm(files, desc=f"   {category}"):
            stats["total"] += 1
            
            try:
                # Extract text
                text = extract_text(file_path)
                
                if not text or len(text) < 100:
                    raise Exception("Text too short or empty")
                
                # Basic data structure
                data = {
                    "category": category,
                    "file_path": file_path,
                    "text": text,
                    "text_length": len(text),
                    "word_count": len(text.split()),
                    "extracted_at": datetime.now().isoformat()
                }
                
                extracted_data.append(data)
                stats["success"] += 1
                stats["by_category"][category]["success"] += 1
                
            except Exception as e:
                stats["failed"] += 1
                stats["by_category"][category]["failed"] += 1
    
    # Save extracted data
    print("\n[*] Saving data...")
    output_file = OUTPUT_DIR / "extracted_resumes_lite.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(extracted_data, f, indent=2, ensure_ascii=False)
    
    print(f"   [OK] Saved to: {output_file}")
    print(f"   [OK] File size: {output_file.stat().st_size / 1024 / 1024:.1f} MB")
    
    # Save stats
    stats_file = OUTPUT_DIR / "extraction_stats_lite.json"
    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(dict(stats), f, indent=2, default=str)
    
    # Print summary
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"Total processed:  {stats['total']}")
    print(f"Successful:       {stats['success']} ({stats['success']/stats['total']*100:.1f}%)")
    print(f"Failed:           {stats['failed']}")
    
    print(f"\n[OK] Text extraction complete!")
    print(f"[*] Next: Run full parsing with ML models on this data")


if __name__ == "__main__":
    main()
