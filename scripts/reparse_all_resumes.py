"""
Re-parse all 2484 resumes with the enhanced experience extractor.
Updates the stored data with improved extraction results.
"""
import json
import sys
import os
import re
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.extractors.enhanced_experience_extractor import EnhancedExperienceExtractor
from services.contact_extractor import ContactExtractor

# Experience section headers
EXPERIENCE_HEADERS = [
    r'(?:professional\s+)?experience',
    r'work\s+(?:experience|history)',
    r'employment\s+(?:history|experience)',
    r'career\s+(?:history|experience)',
    r'professional\s+(?:history|background)',
    r'job\s+history',
    r'positions?\s+held',
]

def find_experience_section(text: str) -> str:
    """Extract the experience section from resume text."""
    lines = text.split('\n')
    
    # Find experience section header
    exp_pattern = '|'.join(EXPERIENCE_HEADERS)
    exp_start = -1
    
    for i, line in enumerate(lines):
        if re.search(rf'\b({exp_pattern})\b', line, re.IGNORECASE):
            exp_start = i
            break
    
    if exp_start == -1:
        # Try to find it in the text anyway
        return text
    
    # Find where experience section ends (next major section)
    section_headers = [
        r'\beducation\b', r'\bskills?\b', r'\bcertifications?\b',
        r'\breferences?\b', r'\bprojects?\b', r'\bsummary\b',
        r'\binterests?\b', r'\bhobbies\b', r'\bawards?\b',
        r'\bvolunteer\b', r'\bpublications?\b'
    ]
    
    exp_end = len(lines)
    for i in range(exp_start + 1, len(lines)):
        line = lines[i].strip()
        if len(line) < 50:  # Only check short lines (likely headers)
            for header in section_headers:
                if re.match(rf'^{header}', line, re.IGNORECASE):
                    exp_end = i
                    break
        if exp_end < len(lines):
            break
    
    return '\n'.join(lines[exp_start:exp_end])

def reparse_all_resumes():
    """Re-parse all resumes with enhanced extractors."""
    
    # Load existing parsed data
    parsed_file = Path("data/training/parsed_resumes_all.json")
    
    if not parsed_file.exists():
        print(f"ERROR: {parsed_file} not found!")
        return
    
    print("=" * 80)
    print("RE-PARSING ALL RESUMES WITH ENHANCED EXTRACTOR")
    print("=" * 80)
    
    with open(parsed_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    total = len(data)
    print(f"\nTotal resumes to process: {total}")
    
    # Initialize extractors
    exp_extractor = EnhancedExperienceExtractor()
    contact_extractor = ContactExtractor()
    
    # Stats tracking
    stats = {
        'processed': 0,
        'experience_extracted': 0,
        'titles_extracted': 0,
        'companies_extracted': 0,
        'dates_extracted': 0,
        'contacts_extracted': 0,
        'skills_present': 0,
        'total_exp_entries': 0,
        'errors': 0
    }
    
    # Backup original data
    backup_file = parsed_file.parent / f"parsed_resumes_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    print(f"Creating backup: {backup_file}")
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(data, f)
    
    print("\nProcessing resumes...")
    
    for i, resume in enumerate(data):
        try:
            text = resume.get('text', '')
            
            if not text:
                stats['errors'] += 1
                continue
            
            # Find experience section
            exp_section = find_experience_section(text)
            
            # Extract experience with enhanced extractor
            experience_entries = exp_extractor.extract_from_section(exp_section)
            
            # Convert to dict format
            experience = [entry.to_dict() for entry in experience_entries]
            
            # Update resume data
            resume['experience'] = experience
            
            # Extract contacts
            contact_info = contact_extractor.extract_contact_info(text)
            resume['contact_info'] = contact_info.to_dict()
            
            # Update stats
            stats['processed'] += 1
            
            if experience:
                stats['experience_extracted'] += 1
                stats['total_exp_entries'] += len(experience)
                
                for exp in experience:
                    if exp.get('title') and exp['title'] != 'Unknown Position':
                        stats['titles_extracted'] += 1
                        break
                
                for exp in experience:
                    if exp.get('company') and exp['company'] != 'Unknown Company':
                        stats['companies_extracted'] += 1
                        break
                
                for exp in experience:
                    if exp.get('dates') or exp.get('start_date'):
                        stats['dates_extracted'] += 1
                        break
            
            if contact_info and (contact_info.emails or contact_info.phones):
                stats['contacts_extracted'] += 1
            
            if resume.get('skills'):
                stats['skills_present'] += 1
            
            # Progress update
            if (i + 1) % 100 == 0:
                pct = (i + 1) / total * 100
                print(f"  Processed {i + 1}/{total} ({pct:.1f}%)")
                
        except Exception as e:
            stats['errors'] += 1
            if stats['errors'] <= 5:
                print(f"  Error on resume {i}: {e}")
    
    # Save updated data
    print(f"\nSaving updated data to {parsed_file}...")
    with open(parsed_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 80)
    print("RE-PARSING COMPLETE - SUMMARY")
    print("=" * 80)
    
    processed = stats['processed']
    print(f"""
Total Resumes: {total}
Processed: {processed}
Errors: {stats['errors']}

EXTRACTION RATES (UPDATED):
  Experience:    {stats['experience_extracted']}/{processed} ({stats['experience_extracted']/processed*100:.1f}%)
  Titles:        {stats['titles_extracted']}/{processed} ({stats['titles_extracted']/processed*100:.1f}%)
  Companies:     {stats['companies_extracted']}/{processed} ({stats['companies_extracted']/processed*100:.1f}%)
  Dates:         {stats['dates_extracted']}/{processed} ({stats['dates_extracted']/processed*100:.1f}%)
  Contacts:      {stats['contacts_extracted']}/{processed} ({stats['contacts_extracted']/processed*100:.1f}%)
  Skills:        {stats['skills_present']}/{processed} ({stats['skills_present']/processed*100:.1f}%)

AVERAGES:
  Avg experience entries per resume: {stats['total_exp_entries']/processed:.2f}

Backup saved to: {backup_file}
Updated data saved to: {parsed_file}
""")
    
    return stats

if __name__ == "__main__":
    reparse_all_resumes()
