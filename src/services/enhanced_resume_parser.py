"""
Enhanced Resume Parser - Complete parsing pipeline integrating all extractors
Week 2-3 Deliverable: Comprehensive information extraction from resumes
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import date, datetime

# Import existing services
import sys
sys.path.append(str(Path(__file__).parent.parent))

from services.pdf_extractor import PDFExtractor
from services.docx_extractor import DOCXExtractor
from services.resume_parser import ResumeParser
from services.section_detector import SectionDetector
from services.contact_extractor import ContactExtractor
from services.name_extractor import NameExtractor
from services.quality_scorer import QualityScorer
from services.ocr_handler import OCRHandler

# Import new extractors
from services.extractors.entity_extractor import EntityExtractor
from services.extractors.skill_extractor import SkillExtractor
from services.extractors.education_extractor import EducationExtractor
from services.extractors.experience_extractor import ExperienceExtractor

logger = logging.getLogger(__name__)


class EnhancedResumeParser:
    """
    Complete resume parsing pipeline with all Week 2-3 features:
    - OCR support
    - 12+ structured fields
    - Skills extraction & normalization
    - Education & experience parsing
    - Date normalization
    - Structured JSON output
    """
    
    def __init__(self):
        """Initialize all extractors"""
        # Week 1 services
        self.pdf_extractor = PDFExtractor()
        self.docx_extractor = DOCXExtractor()
        self.basic_parser = ResumeParser()
        self.section_detector = SectionDetector()
        self.contact_extractor = ContactExtractor()
        self.name_extractor = NameExtractor()
        self.quality_scorer = QualityScorer()
        
        # Week 2 services
        self.ocr_handler = OCRHandler()
        self.entity_extractor = EntityExtractor()
        self.skill_extractor = SkillExtractor()
        self.education_extractor = EducationExtractor()
        self.experience_extractor = ExperienceExtractor()
        
        logger.info("✅ Enhanced Resume Parser initialized with all extractors")
    
    def parse_resume(self, file_path: str, use_ocr: bool = None) -> Dict[str, Any]:
        """
        Complete resume parsing pipeline
        
        Args:
            file_path: Path to resume file
            use_ocr: Force OCR (None = auto-detect)
            
        Returns:
            Comprehensive dictionary with all extracted information
        """
        file_path = Path(file_path)
        
        logger.info(f"📄 Parsing resume: {file_path.name}")
        
        # Step 1: Extract text (with OCR if needed)
        text = self._extract_text(str(file_path), use_ocr)
        
        if not text or len(text) < 100:
            logger.error("❌ Failed to extract sufficient text")
            return self._empty_result(str(file_path), "extraction_failed")
        
        logger.info(f"✅ Extracted {len(text)} characters")
        
        # Step 2: Detect sections
        sections = self.section_detector.detect_sections(text)
        logger.info(f"✅ Detected {len(sections)} sections")
        
        # Step 3: Extract basic information (Week 1)
        name = self.name_extractor.extract_name(text)
        contact_info_obj = self.contact_extractor.extract_contact_info(text)
        contact_info = {
            'email': contact_info_obj.emails[0] if contact_info_obj.emails else None,
            'phone': contact_info_obj.phones[0] if contact_info_obj.phones else None,
            'github': contact_info_obj.github,
            'linkedin': contact_info_obj.linkedin
        }
        
        # Step 4: Extract entities (Week 2)
        entities = self.entity_extractor.extract_entities(text)
        
        # Step 5: Extract education
        education = []
        if 'education' in sections:
            org_names = [e.text for e in entities.get('organizations', [])]
            education = self.education_extractor.extract_from_section(
                sections['education'].content,
                org_names
            )
        
        logger.info(f"✅ Extracted {len(education)} education entries")
        
        # Step 6: Extract experience
        experience = []
        if 'experience' in sections:
            org_names = [e.text for e in entities.get('organizations', [])]
            experience = self.experience_extractor.extract_from_section(
                sections['experience'].content,
                org_names
            )
        
        logger.info(f"✅ Extracted {len(experience)} experience entries")
        
        # Step 7: Extract skills
        section_dict = {k: v.content for k, v in sections.items()}
        skills_result = self.skill_extractor.extract_and_categorize(sections=section_dict)
        
        logger.info(f"✅ Extracted {skills_result.get('total_skills', 0)} skills")
        
        # Step 8: Extract additional fields
        urls = self._extract_urls(text)
        summary = self._extract_summary(sections)
        languages = self._extract_languages(text)
        certifications = self._extract_certifications(sections)
        projects = self._extract_projects(sections)
        publications = self._extract_publications(sections)
        awards = self._extract_awards(sections)
        volunteer = self._extract_volunteer(sections)
        
        # Step 9: Calculate quality score
        quality_obj = self.quality_scorer.assess_quality(str(file_path), text)
        quality = quality_obj.to_dict()
        
        logger.info(f"✅ Quality score: {quality['overall_score']}/100")
        
        # Step 10: Build comprehensive result
        result = {
            'metadata': {
                'file_name': file_path.name,
                'file_type': file_path.suffix.replace('.', '').upper(),
                'extraction_date': datetime.now().isoformat(),
                'extraction_method': 'ocr' if use_ocr else 'text',
                'parser_version': '2.0',
                'quality_score': quality['overall_score'],
                'completeness': self._calculate_completeness(
                    name, contact_info, education, experience, skills_result
                )
            },
            
            'personal_info': {
                'name': name,
                'email': contact_info.get('email'),
                'phone': contact_info.get('phone'),
                'location': self._extract_location(entities),
                'urls': urls
            },
            
            'summary': summary,
            
            'education': [edu.to_dict() for edu in education],
            
            'experience': [exp.to_dict() for exp in experience],
            
            'skills': {
                'total_count': skills_result.get('total_skills', 0),
                'top_skills': skills_result.get('top_skills', []),
                'by_category': skills_result.get('categories', {}),
                'all_skills': skills_result.get('all_skills', [])
            },
            
            'certifications': certifications,
            'projects': projects,
            'publications': publications,
            'awards': awards,
            'volunteer': volunteer,
            'languages': languages,
            
            'sections_detected': [
                {
                    'type': section_type,
                    'confidence': section.confidence,
                    'length': len(section.content)
                }
                for section_type, section in sections.items()
            ],
            
            'quality_assessment': quality
        }
        
        logger.info("✅ Enhanced parsing complete!")
        
        return result
    
    def _extract_text(self, file_path: str, use_ocr: Optional[bool]) -> str:
        """Extract text with OCR support"""
        file_path_obj = Path(file_path)
        
        if file_path_obj.suffix.lower() == '.pdf':
            if use_ocr is None:
                # Auto-detect if OCR needed
                text, method = self.ocr_handler.extract_text_smart(file_path)
                return text
            elif use_ocr:
                return self.ocr_handler.extract_text_with_ocr(file_path)
            else:
                return self.pdf_extractor.extract_text(file_path)
        
        elif file_path_obj.suffix.lower() in ['.docx', '.doc']:
            return self.docx_extractor.extract_text(file_path)
        
        elif file_path_obj.suffix.lower() == '.txt':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        
        return ""
    
    def _extract_location(self, entities: Dict) -> Optional[Dict]:
        """Extract and structure location information"""
        locations = entities.get('locations', [])
        if not locations:
            return None
        
        # Try to parse into city, state, country
        location_text = ', '.join([loc.text for loc in locations])
        
        return {
            'full': location_text,
            'city': locations[0].text if len(locations) > 0 else None,
            'state': locations[1].text if len(locations) > 1 else None,
            'country': locations[-1].text if len(locations) > 2 else None
        }
    
    def _extract_urls(self, text: str) -> Dict[str, str]:
        """Extract social/professional URLs"""
        urls = {}
        
        # LinkedIn
        linkedin_pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/([\w-]+)'
        match = re.search(linkedin_pattern, text, re.IGNORECASE)
        if match:
            urls['linkedin'] = f"https://linkedin.com/in/{match.group(1)}"
        
        # GitHub
        github_pattern = r'(?:https?://)?(?:www\.)?github\.com/([\w-]+)'
        match = re.search(github_pattern, text, re.IGNORECASE)
        if match:
            urls['github'] = f"https://github.com/{match.group(1)}"
        
        # Portfolio/Website
        website_pattern = r'(?:https?://)?([\w-]+\.[\w.-]+)(?:/[\w.-]*)?'
        for match in re.finditer(website_pattern, text):
            url = match.group()
            if 'linkedin' not in url.lower() and 'github' not in url.lower():
                if 'portfolio' not in urls and len(url) > 10:
                    urls['portfolio'] = url if url.startswith('http') else f"https://{url}"
                    break
        
        return urls
    
    def _extract_summary(self, sections: Dict) -> Optional[str]:
        """Extract professional summary"""
        if 'summary' in sections:
            return sections['summary'].content.strip()
        return None
    
    def _extract_languages(self, text: str) -> List[Dict]:
        """Extract spoken languages with proficiency"""
        languages = []
        
        # Common languages
        lang_names = ['English', 'Spanish', 'French', 'German', 'Chinese', 'Hindi', 'Arabic', 
                      'Portuguese', 'Russian', 'Japanese', 'Korean', 'Italian', 'Telugu', 'Tamil']
        
        # Proficiency levels
        proficiencies = ['Native', 'Fluent', 'Professional', 'Conversational', 'Basic', 'Elementary']
        
        for lang in lang_names:
            pattern = rf'{lang}\s*[:\-]?\s*({"|".join(proficiencies)})'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                languages.append({
                    'language': lang,
                    'proficiency': match.group(1)
                })
            elif lang in text:
                # Found language without proficiency
                languages.append({
                    'language': lang,
                    'proficiency': 'Unknown'
                })
        
        return languages
    
    def _extract_certifications(self, sections: Dict) -> List[Dict]:
        """Extract certifications"""
        certs = []
        
        if 'certifications' not in sections:
            return certs
        
        text = sections['certifications'].content
        
        # Common cert names
        cert_patterns = [
            r'AWS Certified[\w\s]+',
            r'Google Cloud[\w\s]+',
            r'Microsoft Certified[\w\s]+',
            r'Certified[\w\s]+Professional',
            r'PMP',
            r'Certified Kubernetes[\w\s]+',
        ]
        
        for pattern in cert_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                certs.append({
                    'name': match.group().strip(),
                    'issuer': self._guess_issuer(match.group())
                })
        
        return certs
    
    def _guess_issuer(self, cert_name: str) -> str:
        """Guess certification issuer"""
        cert_lower = cert_name.lower()
        if 'aws' in cert_lower:
            return 'Amazon Web Services'
        elif 'google' in cert_lower:
            return 'Google Cloud'
        elif 'microsoft' in cert_lower or 'azure' in cert_lower:
            return 'Microsoft'
        elif 'kubernetes' in cert_lower:
            return 'Cloud Native Computing Foundation'
        return 'Unknown'
    
    def _extract_projects(self, sections: Dict) -> List[Dict]:
        """Extract projects"""
        projects = []
        
        if 'projects' not in sections:
            return projects
        
        text = sections['projects'].content
        
        # Split by bullet points or double newlines
        blocks = re.split(r'\n\s*\n|•|▪|-\s', text)
        
        for block in blocks:
            if len(block.strip()) > 30:
                # Extract project name (usually first line or capitalized)
                lines = block.strip().split('\n')
                name = lines[0].strip() if lines else "Unnamed Project"
                
                projects.append({
                    'name': name[:100],
                    'description': block.strip()[:300]
                })
        
        return projects[:10]  # Limit to 10 projects
    
    def _extract_publications(self, sections: Dict) -> List[Dict]:
        """Extract publications"""
        pubs = []
        
        if 'publications' not in sections:
            return pubs
        
        text = sections['publications'].content
        
        # Look for publication patterns
        # Common format: "Title", Authors, Conference/Journal, Year
        blocks = re.split(r'\n\s*\n|•|▪', text)
        
        for block in blocks:
            if len(block.strip()) > 30:
                pubs.append({
                    'title': block.strip()[:200]
                })
        
        return pubs[:10]
    
    def _extract_awards(self, sections: Dict) -> List[str]:
        """Extract awards and achievements"""
        awards = []
        
        if 'achievements' not in sections:
            return awards
        
        text = sections['achievements'].content
        
        # Split by bullets
        blocks = re.split(r'•|▪|-\s', text)
        
        for block in blocks:
            block = block.strip()
            if len(block) > 10 and len(block) < 200:
                awards.append(block)
        
        return awards[:15]
    
    def _extract_volunteer(self, sections: Dict) -> List[Dict]:
        """Extract volunteer experience"""
        volunteer = []
        
        if 'volunteer' not in sections:
            return volunteer
        
        text = sections['volunteer'].content
        
        blocks = re.split(r'\n\s*\n', text)
        
        for block in blocks:
            if len(block.strip()) > 30:
                volunteer.append({
                    'description': block.strip()[:300]
                })
        
        return volunteer[:5]
    
    def _calculate_completeness(self, name, contact, education, experience, skills) -> int:
        """Calculate how complete the resume information is (0-100)"""
        score = 0
        
        if name:
            score += 10
        if contact.get('email'):
            score += 15
        if contact.get('phone'):
            score += 10
        if education:
            score += 20
        if experience:
            score += 25
        if skills.get('total_skills', 0) > 0:
            score += 20
        
        return min(100, score)
    
    def _empty_result(self, file_path: str, error: str) -> Dict:
        """Return empty result structure"""
        return {
            'metadata': {
                'file_name': Path(file_path).name,
                'error': error,
                'quality_score': 0
            },
            'personal_info': {},
            'education': [],
            'experience': [],
            'skills': {}
        }
    
    def save_to_json(self, result: Dict, output_path: str):
        """Save parsing result to JSON file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Saved results to {output_path}")


# Import re at top
import re


def test_enhanced_parser():
    """Test enhanced parser on sample resume"""
    parser = EnhancedResumeParser()
    
    print("\n" + "="*70)
    print("🚀 Testing Enhanced Resume Parser (Week 2-3)")
    print("="*70 + "\n")
    
    # Test on user's resume
    resume_path = "data/sample_resumes/real_world/my_resume.pdf"
    
    if not Path(resume_path).exists():
        print(f"❌ Resume not found: {resume_path}")
        print("   Please provide a test resume")
        return
    
    result = parser.parse_resume(resume_path)
    
    print(f"\n📊 Parsing Results Summary:")
    print("="*70)
    print(f"Name: {result['personal_info'].get('name', 'N/A')}")
    print(f"Email: {result['personal_info'].get('email', 'N/A')}")
    print(f"Phone: {result['personal_info'].get('phone', 'N/A')}")
    print(f"Quality Score: {result['metadata']['quality_score']}/100")
    print(f"Completeness: {result['metadata']['completeness']}%")
    print(f"\nEducation Entries: {len(result['education'])}")
    print(f"Experience Entries: {len(result['experience'])}")
    print(f"Skills Extracted: {result['skills']['total_count']}")
    print(f"Sections Detected: {len(result['sections_detected'])}")
    
    # Show top skills
    if result['skills']['top_skills']:
        print(f"\nTop 5 Skills:")
        for skill in result['skills']['top_skills'][:5]:
            print(f"  • {skill['name']} ({skill['category']})")
    
    # Save to JSON
    output_path = "data/parsed_output.json"
    parser.save_to_json(result, output_path)
    
    print(f"\n✅ Complete! Results saved to: {output_path}")


if __name__ == "__main__":
    test_enhanced_parser()
