"""
Week 1 Comprehensive Test

Tests all Week 1 features together:
- PDF/DOCX/TXT extraction
- Section detection
- Contact extraction
- Name extraction
- Quality assessment
"""

from pathlib import Path
from src.services.resume_parser import ResumeParser


def test_week1_features():
    """Test all Week 1 features on sample resumes"""
    
    # Initialize parser with all Week 1 features
    parser = ResumeParser(
        detect_sections=True,
        extract_contact=True,
        extract_name=True,
        assess_quality=True
    )
    
    # Test files
    test_files = [
        "data/sample_resumes/john_doe_simple.pdf",
        "data/sample_resumes/sarah_chen_data_scientist.pdf",
        "data/sample_resumes/michael_rodriguez_pm.pdf"
    ]
    
    print("=" * 80)
    print("WEEK 1 COMPREHENSIVE TEST")
    print("Testing all extraction features together")
    print("=" * 80)
    
    for file_path in test_files:
        if not Path(file_path).exists():
            print(f"\n❌ File not found: {file_path}")
            continue
        
        print(f"\n\n📄 {Path(file_path).name}")
        print("-" * 80)
        
        try:
            # Parse resume
            result = parser.parse(file_path)
            
            if not result.get('success'):
                print(f"❌ Parsing failed: {result.get('error')}")
                continue
            
            # Basic info
            print(f"\n📋 BASIC INFO:")
            print(f"  File Type: {result.get('file_type', 'unknown').upper()}")
            print(f"  File Size: {result.get('file_size', 0):,} bytes")
            print(f"  Words: {result.get('word_count', 0):,}")
            print(f"  Characters: {result.get('char_count', 0):,}")
            print(f"  Extraction: {result.get('extraction_method', 'unknown')}")
            
            # Name extraction
            if result.get('name'):
                print(f"\n👤 NAME:")
                print(f"  {result['name']}")
            
            # Contact information
            if result.get('contact_info'):
                contact = result['contact_info']
                print(f"\n📞 CONTACT INFO:")
                
                if contact.get('emails'):
                    print(f"  Email: {', '.join(contact['emails'])}")
                
                if contact.get('phones'):
                    print(f"  Phone: {', '.join(contact['phones'])}")
                
                if contact.get('linkedin'):
                    print(f"  LinkedIn: {contact['linkedin']}")
                
                if contact.get('location'):
                    print(f"  Location: {contact['location']}")
            
            # Sections
            if result.get('sections_found'):
                print(f"\n📂 SECTIONS DETECTED ({len(result['sections_found'])}):")
                sections = result.get('sections', {})
                
                for section_name in result['sections_found']:
                    section = sections.get(section_name, {})
                    confidence = section.get('confidence', 0)
                    char_count = section.get('char_count', 0)
                    raw_header = section.get('raw_header', section_name)
                    
                    # Emoji for different sections
                    emoji = {
                        'experience': '💼',
                        'education': '🎓',
                        'skills': '🔧',
                        'summary': '📝',
                        'projects': '🚀',
                        'certifications': '📜',
                        'languages': '🌍',
                        'interests': '⚡',
                        'publications': '📚',
                        'awards': '🏆'
                    }.get(section_name, '📄')
                    
                    print(f"  {emoji} {raw_header}")
                    print(f"     Confidence: {confidence:.1%} | Length: {char_count} chars")
                    
                    # Show snippet of content
                    content = section.get('content', '')
                    if content:
                        snippet = ' '.join(content.split()[:15])
                        if len(content.split()) > 15:
                            snippet += "..."
                        print(f"     Preview: {snippet}")
            
            # Quality assessment (PDF only)
            if result.get('quality'):
                quality = result['quality']
                print(f"\n📊 QUALITY ASSESSMENT:")
                print(f"  Overall Score: {quality['overall_score']:.1f}/100")
                
                # Score breakdown
                print(f"  ├─ Extraction:  {quality['extraction_quality']:.1f}/100")
                print(f"  ├─ Completeness: {quality['completeness']:.1f}/100")
                print(f"  ├─ Formatting:  {quality['formatting_quality']:.1f}/100")
                print(f"  └─ Readability: {quality['readability']:.1f}/100")
                
                # Document properties
                print(f"\n  Document Properties:")
                print(f"  ├─ Scanned: {'Yes' if quality['is_scanned'] else 'No'}")
                print(f"  └─ Has Images: {'Yes' if quality['has_images'] else 'No'}")
                
                # Issues and recommendations
                if quality.get('issues'):
                    print(f"\n  ⚠️  Issues ({len(quality['issues'])}):")
                    for issue in quality['issues'][:3]:
                        print(f"     • {issue}")
                    if len(quality['issues']) > 3:
                        print(f"     ... and {len(quality['issues']) - 3} more")
                
                if quality.get('recommendations'):
                    print(f"\n  💡 Recommendations ({len(quality['recommendations'])}):")
                    for rec in quality['recommendations'][:3]:
                        print(f"     • {rec}")
                    if len(quality['recommendations']) > 3:
                        print(f"     ... and {len(quality['recommendations']) - 3} more")
            
            # Overall assessment
            print(f"\n✅ WEEK 1 FEATURES:")
            features_status = []
            features_status.append(("Text Extraction", result.get('success', False)))
            features_status.append(("Name Detection", bool(result.get('name'))))
            features_status.append(("Contact Info", bool(result.get('contact_info'))))
            features_status.append(("Section Detection", bool(result.get('sections_found'))))
            features_status.append(("Quality Assessment", bool(result.get('quality'))))
            
            for feature_name, status in features_status:
                icon = "✅" if status else "❌"
                print(f"  {icon} {feature_name}")
            
        except Exception as e:
            print(f"❌ Error processing file: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("✅ Week 1 comprehensive test completed!")
    print("=" * 80)


if __name__ == "__main__":
    test_week1_features()
