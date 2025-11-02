"""
Show Full Section Content for Meher's Resume
"""

from pathlib import Path
from src.services.resume_parser import ResumeParser


def show_section_content():
    """Display full content of each section"""
    
    resume_path = "data/sample_resumes/real_world/my_resume.pdf"
    
    parser = ResumeParser(detect_sections=True)
    result = parser.parse(resume_path)
    
    if not result.get('success'):
        print(f"❌ Error: {result.get('error')}")
        return
    
    print("=" * 80)
    print("MEHER VENKAT RAMAN - FULL SECTION CONTENT")
    print("=" * 80)
    print()
    
    sections = result.get('sections', {})
    sections_found = result.get('sections_found', [])
    
    for section_name in sections_found:
        section = sections.get(section_name, {})
        header = section.get('raw_header', section_name)
        content = section.get('content', '')
        confidence = section.get('confidence', 0)
        
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
        
        print(f"{emoji} {header.upper()}")
        print(f"Section: {section_name} | Confidence: {confidence:.0%}")
        print("-" * 80)
        
        if content.strip():
            print(content.strip())
        else:
            print("(Header detected but content appears in following section)")
        
        print()
        print()


if __name__ == "__main__":
    show_section_content()
