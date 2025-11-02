"""
Detailed Test for Meher's Resume

Shows all extracted information from my_resume.pdf
"""

from pathlib import Path
from src.services.resume_parser import ResumeParser
import json


def test_my_resume():
    """Test and display all extracted information from my_resume.pdf"""
    
    resume_path = "data/sample_resumes/real_world/my_resume.pdf"
    
    if not Path(resume_path).exists():
        print(f"❌ Resume not found: {resume_path}")
        return
    
    print("=" * 80)
    print("DETAILED ANALYSIS: MEHER VENKAT RAMAN'S RESUME")
    print("=" * 80)
    print()
    
    # Initialize parser with all features
    parser = ResumeParser(
        detect_sections=True,
        extract_contact=True,
        extract_name=True,
        assess_quality=True
    )
    
    # Parse resume
    print("⏳ Parsing resume...")
    result = parser.parse(resume_path)
    
    if not result.get('success'):
        print(f"❌ Parsing failed: {result.get('error')}")
        return
    
    print("✅ Parsing successful!\n")
    
    # ===========================================
    # 1. BASIC INFORMATION
    # ===========================================
    print("📋 BASIC INFORMATION")
    print("-" * 80)
    print(f"File Name:       {result.get('file_name')}")
    print(f"File Size:       {result.get('file_size'):,} bytes ({result.get('file_size')/1024:.1f} KB)")
    print(f"File Type:       {result.get('file_type', 'unknown').upper()}")
    print(f"Pages:           {result.get('metadata', {}).get('pages', 'N/A')}")
    print(f"Extraction:      {result.get('extraction_method', 'unknown')}")
    print(f"Characters:      {result.get('char_count', 0):,}")
    print(f"Words:           {result.get('word_count', 0):,}")
    print()
    
    # ===========================================
    # 2. PERSONAL INFORMATION
    # ===========================================
    print("👤 PERSONAL INFORMATION")
    print("-" * 80)
    
    # Name
    name = result.get('name')
    print(f"Full Name:       {name if name else '❌ Not detected'}")
    print()
    
    # Contact Information
    contact = result.get('contact_info', {})
    
    print("📧 Email:")
    emails = contact.get('emails', [])
    if emails:
        for email in emails:
            print(f"  ✅ {email}")
    else:
        print("  ❌ Not detected")
    print()
    
    print("📱 Phone:")
    phones = contact.get('phones', [])
    if phones:
        for phone in phones:
            print(f"  ✅ {phone}")
    else:
        print("  ❌ Not detected")
    print()
    
    print("🔗 LinkedIn:")
    linkedin = contact.get('linkedin')
    print(f"  {'✅ ' + linkedin if linkedin else '❌ Not detected'}")
    print()
    
    print("💻 GitHub:")
    github = contact.get('github')
    print(f"  {'✅ ' + github if github else '❌ Not detected'}")
    print()
    
    print("🌐 Website/Portfolio:")
    website = contact.get('website')
    print(f"  {'✅ ' + website if website else '❌ Not detected'}")
    print()
    
    print("📍 Location:")
    location = contact.get('location')
    print(f"  {'✅ ' + location if location else '❌ Not detected'}")
    print()
    
    # ===========================================
    # 3. SECTIONS DETECTED
    # ===========================================
    print("📂 RESUME SECTIONS")
    print("-" * 80)
    
    sections_found = result.get('sections_found', [])
    sections = result.get('sections', {})
    
    print(f"Total sections detected: {len(sections_found)}\n")
    
    if sections_found:
        for i, section_name in enumerate(sections_found, 1):
            section = sections.get(section_name, {})
            header = section.get('raw_header', section_name)
            content = section.get('content', '')
            confidence = section.get('confidence', 0)
            char_count = section.get('char_count', 0)
            
            # Emoji mapping
            emoji_map = {
                'experience': '💼',
                'education': '🎓',
                'skills': '🔧',
                'summary': '📝',
                'projects': '🚀',
                'certifications': '📜',
                'languages': '🌍',
                'interests': '⚡',
                'publications': '📚',
                'awards': '🏆',
                'achievements': '🏅'
            }
            emoji = emoji_map.get(section_name, '📄')
            
            print(f"{i}. {emoji} {header.upper()}")
            print(f"   Section Type: {section_name}")
            print(f"   Confidence: {confidence:.1%}")
            print(f"   Length: {char_count} characters")
            
            # Show content preview
            if content:
                # Clean and limit preview
                preview = ' '.join(content.split())
                if len(preview) > 150:
                    preview = preview[:150] + "..."
                print(f"   Preview: {preview}")
            else:
                print(f"   Content: (Header only, content in next section)")
            print()
    else:
        print("❌ No sections detected")
    print()
    
    # ===========================================
    # 4. QUALITY ASSESSMENT
    # ===========================================
    quality = result.get('quality')
    if quality:
        print("📊 QUALITY ASSESSMENT")
        print("-" * 80)
        
        overall = quality.get('overall_score', 0)
        print(f"Overall Score:      {overall:.1f}/100  ", end="")
        if overall >= 90:
            print("🌟 EXCELLENT")
        elif overall >= 80:
            print("✅ VERY GOOD")
        elif overall >= 70:
            print("👍 GOOD")
        elif overall >= 60:
            print("⚠️  FAIR")
        else:
            print("❌ NEEDS IMPROVEMENT")
        print()
        
        print("Score Breakdown:")
        print(f"  Extraction Quality:   {quality.get('extraction_quality', 0):.1f}/100")
        print(f"  Completeness:         {quality.get('completeness', 0):.1f}/100")
        print(f"  Formatting Quality:   {quality.get('formatting_quality', 0):.1f}/100")
        print(f"  Readability:          {quality.get('readability', 0):.1f}/100")
        print()
        
        print("Document Properties:")
        print(f"  Scanned PDF:          {'Yes ⚠️' if quality.get('is_scanned') else 'No ✅'}")
        print(f"  Contains Images:      {'Yes' if quality.get('has_images') else 'No'}")
        print()
        
        # Issues
        issues = quality.get('issues', [])
        if issues:
            print(f"⚠️  Issues Found ({len(issues)}):")
            for issue in issues:
                print(f"  • {issue}")
            print()
        
        # Recommendations
        recommendations = quality.get('recommendations', [])
        if recommendations:
            print(f"💡 Recommendations ({len(recommendations)}):")
            for rec in recommendations:
                print(f"  • {rec}")
            print()
    
    # ===========================================
    # 5. FULL TEXT PREVIEW
    # ===========================================
    print("📄 RESUME TEXT PREVIEW")
    print("-" * 80)
    text = result.get('text', '')
    if text:
        # Show first 500 characters
        preview = text[:500]
        print(preview)
        if len(text) > 500:
            print(f"\n... (showing first 500 of {len(text)} total characters)")
    else:
        print("❌ No text extracted")
    print()
    
    # ===========================================
    # 6. SUMMARY & RECOMMENDATIONS
    # ===========================================
    print("=" * 80)
    print("📌 SUMMARY")
    print("=" * 80)
    
    print("\n✅ Successfully Extracted:")
    extracted_items = []
    if name:
        extracted_items.append("✓ Name")
    if contact.get('emails'):
        extracted_items.append("✓ Email")
    if contact.get('phones'):
        extracted_items.append("✓ Phone")
    if contact.get('github'):
        extracted_items.append("✓ GitHub")
    if sections_found:
        extracted_items.append(f"✓ {len(sections_found)} Sections")
    
    for item in extracted_items:
        print(f"  {item}")
    
    print("\n⚠️  Missing/Not Detected:")
    missing_items = []
    if not contact.get('linkedin'):
        missing_items.append("✗ LinkedIn profile")
    if not contact.get('website'):
        missing_items.append("✗ Portfolio/Website")
    if not contact.get('location') or contact.get('location') == 'Engineering, University':
        missing_items.append("✗ Complete location (City, State)")
    
    if missing_items:
        for item in missing_items:
            print(f"  {item}")
    else:
        print("  None - All information extracted!")
    
    print("\n💬 Overall Assessment:")
    if quality:
        score = quality.get('overall_score', 0)
        if score >= 90:
            print("  🌟 Your resume is EXCELLENT! All major information extracted successfully.")
        elif score >= 80:
            print("  ✅ Your resume is VERY GOOD! Minor improvements possible.")
        else:
            print("  👍 Your resume is GOOD. See recommendations above for improvements.")
    
    print("\n" + "=" * 80)
    print("✅ Analysis complete!")
    print("=" * 80)


if __name__ == "__main__":
    test_my_resume()
