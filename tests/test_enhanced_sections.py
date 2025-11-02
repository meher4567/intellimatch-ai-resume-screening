"""
Test Enhanced Section Detection

Shows all sections detected with the enhanced detector
"""

from pathlib import Path
from src.services.resume_parser import ResumeParser


def test_enhanced_sections():
    """Test enhanced section detection on various resumes"""
    
    test_files = [
        "data/sample_resumes/real_world/my_resume.pdf",
        "data/sample_resumes/john_doe_simple.pdf",
        "data/sample_resumes/sarah_chen_data_scientist.pdf",
        "data/sample_resumes/real_world/github_awesome_cv.pdf",
    ]
    
    parser = ResumeParser(detect_sections=True)
    
    print("=" * 80)
    print("ENHANCED SECTION DETECTION TEST")
    print("=" * 80)
    print(f"\nNow detecting {len(parser.section_detector.SECTION_PATTERNS)} section types:\n")
    
    # List all supported sections
    section_types = list(parser.section_detector.SECTION_PATTERNS.keys())
    for i, section in enumerate(section_types, 1):
        print(f"{i:2d}. {section.title()}")
    
    print("\n" + "=" * 80)
    print()
    
    for file_path in test_files:
        if not Path(file_path).exists():
            print(f"⚠️  File not found: {file_path}\n")
            continue
        
        print(f"📄 {Path(file_path).name}")
        print("-" * 80)
        
        result = parser.parse(file_path)
        
        if not result.get('success'):
            print(f"❌ Error: {result.get('error')}\n")
            continue
        
        sections_found = result.get('sections_found', [])
        sections = result.get('sections', {})
        
        print(f"Sections detected: {len(sections_found)}\n")
        
        if sections_found:
            for section_name in sections_found:
                section = sections.get(section_name, {})
                header = section.get('raw_header', section_name)
                confidence = section.get('confidence', 0)
                char_count = section.get('char_count', 0)
                
                emoji_map = {
                    'experience': '💼', 'education': '🎓', 'skills': '🔧',
                    'summary': '📝', 'projects': '🚀', 'certifications': '📜',
                    'languages': '🌍', 'interests': '⚡', 'publications': '📚',
                    'awards': '🏆', 'achievements': '🏅', 'volunteer': '🤝',
                    'leadership': '👑', 'conferences': '🎤', 'patents': '💡',
                    'references': '✉️', 'activities': '🎯', 'coursework': '📖',
                    'internships': '🎓', 'research': '🔬', 'teaching': '👨‍🏫',
                }
                emoji = emoji_map.get(section_name, '📄')
                
                print(f"  {emoji} {header}")
                print(f"     Type: {section_name} | Confidence: {confidence:.0%} | Length: {char_count} chars")
        else:
            print("  No sections detected")
        
        print()


if __name__ == "__main__":
    test_enhanced_sections()
