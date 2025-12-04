"""
Resume Parser - Main Interface
Unified parser for PDF and DOCX resume files
"""

from pathlib import Path
from typing import Dict, Optional
import logging

from .pdf_extractor import PDFExtractor, extract_text_from_pdf
from .docx_extractor import DOCXExtractor, extract_text_from_docx
from .section_detector import SectionDetector
from .contact_extractor import ContactExtractor
from .name_extractor import NameExtractor
from .quality_scorer import QualityScorer
from .extractors.experience_extractor import ExperienceExtractor

# Import ML-based extractors
from ..ml import HybridNameExtractor, SkillEmbedder, OrganizationExtractor, DynamicSkillExtractor
from ..ml.enhanced_skill_extractor import EnhancedSkillExtractor
from ..ml.experience_timeline import analyze_career_timeline

logger = logging.getLogger(__name__)


class ResumeParser:
    """
    Main resume parser that handles multiple file formats
    """
    
    def __init__(self, detect_sections: bool = True, extract_contact: bool = True, extract_name: bool = True, assess_quality: bool = True, use_ml: bool = True):
        """Initialize resume parser with extractors"""
        self.pdf_extractor = PDFExtractor()
        self.docx_extractor = DOCXExtractor()
        self.section_detector = SectionDetector() if detect_sections else None
        self.contact_extractor = ContactExtractor() if extract_contact else None
        self.experience_extractor = ExperienceExtractor()
        
        # Use ML-based extractors if enabled
        self.use_ml = use_ml
        if use_ml and extract_name:
            logger.info("Using ML-based extractors (name, skills, organizations)")
            self.name_extractor = HybridNameExtractor()
            # Use both: Dynamic extractor for broad coverage + Semantic for matching
            self.dynamic_skill_extractor = DynamicSkillExtractor()
            self.skill_extractor = SkillEmbedder()  # Keep for semantic matching
            self.org_extractor = OrganizationExtractor()
            # Add enhanced extractors
            self.enhanced_skill_extractor = EnhancedSkillExtractor()
        else:
            logger.info("Using rule-based extractors only")
            self.name_extractor = NameExtractor() if extract_name else None
            self.dynamic_skill_extractor = None
            self.skill_extractor = None
            self.org_extractor = None
            self.enhanced_skill_extractor = None
        
        self.quality_scorer = QualityScorer() if assess_quality else None
        
        self.supported_formats = {
            '.pdf': 'pdf',
            '.docx': 'docx',
            '.txt': 'txt'
        }
    
    def parse(self, file_path: str) -> Dict:
        """
        Parse resume file and extract text content
        
        Args:
            file_path: Path to resume file (PDF, DOCX, or TXT)
            
        Returns:
            Dict with:
                - text: Extracted text content
                - file_type: Type of file (pdf/docx/txt)
                - file_name: Name of the file
                - file_size: Size in bytes
                - extraction_method: Method used for extraction
                - success: Whether extraction was successful
                - error: Error message if failed
                - metadata: Additional metadata (pages, author, etc.)
        """
        file_path = Path(file_path).resolve()
        
        # Validate file exists
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return self._create_error_result(file_path, "File not found")
        
        # Get file info
        file_ext = file_path.suffix.lower()
        file_size = file_path.stat().st_size
        
        # Validate file format
        if file_ext not in self.supported_formats:
            logger.error(f"Unsupported file format: {file_ext}")
            return self._create_error_result(file_path, f"Unsupported format: {file_ext}")
        
        logger.info(f"Parsing resume: {file_path.name} ({file_ext}, {file_size} bytes)")
        
        try:
            # Extract text based on file type
            if file_ext == '.pdf':
                result = self._parse_pdf(file_path)
            elif file_ext == '.docx':
                result = self._parse_docx(file_path)
            elif file_ext == '.txt':
                result = self._parse_txt(file_path)
            else:
                result = self._create_error_result(file_path, "Unknown format")
            
            # Add file info
            result.update({
                'file_name': file_path.name,
                'file_size': file_size,
                'file_type': self.supported_formats[file_ext],
                'file_path': str(file_path)
            })
            
            # Clean and preprocess text
            if result.get('success') and result.get('text'):
                result['text'] = self._preprocess_text(result['text'])
                result['char_count'] = len(result['text'])
                result['word_count'] = len(result['text'].split())
                
                # Detect sections if enabled
                if self.section_detector:
                    sections = self.section_detector.detect_sections(result['text'])
                    result['sections'] = {
                        name: {
                            'raw_header': section.raw_header,
                            'content': section.content,
                            'confidence': section.confidence,
                            'char_count': len(section.content)
                        }
                        for name, section in sections.items()
                    }
                    result['sections_found'] = list(sections.keys())
                
                # Extract contact information if enabled
                if self.contact_extractor:
                    contact_info = self.contact_extractor.extract_contact_info(result['text'])
                    result['contact_info'] = contact_info.to_dict()
                
                # Extract experience from experience section AND publications section
                # (publications often contains research positions)
                experience_entries = []
                if self.experience_extractor and 'sections' in result:
                    # Get company names from organizations if available
                    company_names = None
                    if 'organizations' in result and 'companies' in result['organizations']:
                        company_names = result['organizations']['companies']
                    
                    # Extract from experience section
                    if 'experience' in result['sections']:
                        exp_section_text = result['sections']['experience']['content']
                        entries = self.experience_extractor.extract_from_section(
                            exp_section_text, 
                            company_names
                        )
                        experience_entries.extend(entries)
                    
                    # Also check publications section (often contains research experience)
                    if 'publications' in result['sections']:
                        pub_section_text = result['sections']['publications']['content']
                        # Check if it has experience-like content (dates, companies)
                        if '202' in pub_section_text or '201' in pub_section_text:  # Year indicators
                            pub_entries = self.experience_extractor.extract_from_section(
                                pub_section_text, 
                                company_names
                            )
                            experience_entries.extend(pub_entries)
                    
                    result['experience'] = [exp.to_dict() for exp in experience_entries]
                    result['total_years_experience'] = sum(
                        exp.duration_months or 0 for exp in experience_entries
                    ) / 12.0
                else:
                    result['experience'] = []
                    result['total_years_experience'] = 0
                
                # Extract name if enabled
                if self.name_extractor:
                    if self.use_ml:
                        # Use hybrid ML+rules extraction
                        name_result = self.name_extractor.extract_with_details(result['text'])
                        result['name'] = name_result['name']
                        result['name_extraction'] = {
                            'method': name_result['method'],
                            'confidence': name_result.get('confidence'),
                            'ml_enabled': True
                        }
                    else:
                        # Use rule-based extraction
                        name = self.name_extractor.extract_name(result['text'])
                        result['name'] = name
                        result['name_extraction'] = {
                            'method': 'rules',
                            'ml_enabled': False
                        }
                
                # Extract skills using dynamic + semantic matching if ML enabled
                if self.use_ml and self.dynamic_skill_extractor:
                    # Use dynamic extractor for broad skill extraction
                    sections_dict = {name: section['content'] for name, section in result.get('sections', {}).items()} if 'sections' in result else None
                    dynamic_skills = self.dynamic_skill_extractor.extract_skills(result['text'], sections_dict)
                    
                    result['skills'] = {
                        'all_skills': dynamic_skills['all_skills'],
                        'by_category': {
                            'technical': dynamic_skills.get('technical_skills', []),
                            'soft': dynamic_skills.get('soft_skills', []),
                            'tools': dynamic_skills.get('tools', []),
                            'methodologies': dynamic_skills.get('methodologies', [])
                        },
                        'count': dynamic_skills['count'],
                        'extraction_method': 'dynamic_ner_pattern'
                    }
                    
                    # Add enhanced skill extraction with proficiency levels
                    if self.enhanced_skill_extractor:
                        # Prepare resume data structure for enhanced extractor
                        resume_data = {
                            'text': result['text'],
                            'sections': sections_dict,
                            'experience': result.get('experience', [])
                        }
                        enhanced_result = self.enhanced_skill_extractor.extract_skills_with_metadata(resume_data)
                        result['skills']['enhanced'] = enhanced_result.get('skills_with_proficiency', [])
                        
                        # Calculate proficiency summary
                        skills_list = enhanced_result.get('skills_with_proficiency', [])
                        result['skills']['proficiency_summary'] = {
                            'expert': len([s for s in skills_list if s.get('proficiency') == 'expert']),
                            'proficient': len([s for s in skills_list if s.get('proficiency') == 'proficient']),
                            'intermediate': len([s for s in skills_list if s.get('proficiency') == 'intermediate']),
                            'beginner': len([s for s in skills_list if s.get('proficiency') == 'beginner'])
                        }
                        
                        # Add additional enhanced metadata
                        result['skills']['skill_sources'] = enhanced_result.get('skill_sources', {})
                        result['skills']['skill_years'] = enhanced_result.get('skill_years', {})
                        
                        # Add skill portfolio analysis
                        portfolio = self.enhanced_skill_extractor.analyze_skill_portfolio(skills_list)
                        result['skills']['portfolio_analysis'] = portfolio
                
                # Extract organizations/companies if ML enabled
                if self.use_ml and self.org_extractor:
                    # Sections are already dicts with 'content' key
                    sections_dict = {name: section['content'] for name, section in result.get('sections', {}).items()} if 'sections' in result else None
                    orgs_result = self.org_extractor.extract_organizations(result['text'], sections_dict)
                    companies = self.org_extractor.extract_companies(result['text'], sections_dict)
                    universities = self.org_extractor.extract_universities(result['text'], sections_dict)
                    org_summary = self.org_extractor.get_organization_summary(orgs_result)
                    
                    result['organizations'] = {
                        'all': [o.name for o in orgs_result],
                        'companies': [c.name for c in companies],
                        'universities': [u.name for u in universities],
                        'detailed': [{'name': o.name, 'category': o.category, 
                                     'confidence': o.confidence, 'section': o.section} 
                                    for o in orgs_result],
                        'summary': org_summary,
                        'extraction_method': 'ner_ml'
                    }
                    
                    # Add career timeline analysis
                    timeline_resume_data = {
                        'text': result['text'],
                        'sections': sections_dict,
                        'experience': result.get('experience', [])
                    }
                    timeline_analysis = analyze_career_timeline(timeline_resume_data)
                    result['career_timeline'] = timeline_analysis
                
                # Assess quality if enabled (only for PDFs)
                if self.quality_scorer and result.get('file_type') == 'pdf':
                    quality = self.quality_scorer.assess_quality(str(file_path), result['text'])
                    result['quality'] = quality.to_dict()
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}", exc_info=True)
            return self._create_error_result(file_path, str(e))
    
    def _parse_pdf(self, file_path: Path) -> Dict:
        """Parse PDF file"""
        try:
            result = self.pdf_extractor.extract_text(str(file_path))
            metadata = self.pdf_extractor.get_metadata(str(file_path))
            
            success = len(result.get('text', '')) > 0
            
            return {
                'text': result.get('text', ''),
                'extraction_method': result.get('method', 'unknown'),
                'success': success,
                'error': None if success else 'No text extracted',
                'metadata': metadata
            }
        except Exception as e:
            logger.error(f"PDF parsing failed: {e}")
            return self._create_error_result(file_path, f"PDF error: {e}")
    
    def _parse_docx(self, file_path: Path) -> Dict:
        """Parse DOCX file"""
        try:
            result = self.docx_extractor.extract_text(str(file_path))
            metadata = self.docx_extractor.get_document_properties(str(file_path))
            
            success = len(result.get('text', '')) > 0
            
            return {
                'text': result.get('text', ''),
                'extraction_method': result.get('method', 'python-docx'),
                'success': success,
                'error': None if success else 'No text extracted',
                'metadata': metadata
            }
        except Exception as e:
            logger.error(f"DOCX parsing failed: {e}")
            return self._create_error_result(file_path, f"DOCX error: {e}")
    
    def _parse_txt(self, file_path: Path) -> Dict:
        """Parse TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            return {
                'text': text,
                'extraction_method': 'text',
                'success': True,
                'error': None,
                'metadata': {'encoding': 'utf-8'}
            }
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    text = f.read()
                return {
                    'text': text,
                    'extraction_method': 'text',
                    'success': True,
                    'error': None,
                    'metadata': {'encoding': 'latin-1'}
                }
            except Exception as e:
                logger.error(f"TXT parsing failed: {e}")
                return self._create_error_result(file_path, f"TXT error: {e}")
    
    def _preprocess_text(self, text: str) -> str:
        """
        Basic text preprocessing
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove excessive spaces
            line = ' '.join(line.split())
            if line:
                cleaned_lines.append(line)
        
        # Join with single newlines
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Remove multiple consecutive newlines (max 2)
        while '\n\n\n' in cleaned_text:
            cleaned_text = cleaned_text.replace('\n\n\n', '\n\n')
        
        return cleaned_text.strip()
    
    def _create_error_result(self, file_path: Path, error_msg: str) -> Dict:
        """Create error result dict"""
        return {
            'text': '',
            'file_name': file_path.name if isinstance(file_path, Path) else str(file_path),
            'file_size': 0,
            'file_type': 'unknown',
            'extraction_method': None,
            'success': False,
            'error': error_msg,
            'metadata': {}
        }
    
    def batch_parse(self, file_paths: list) -> Dict[str, Dict]:
        """
        Parse multiple resume files
        
        Args:
            file_paths: List of file paths to parse
            
        Returns:
            Dict mapping file names to parse results
        """
        results = {}
        
        logger.info(f"Batch parsing {len(file_paths)} files")
        
        for file_path in file_paths:
            result = self.parse(file_path)
            results[result['file_name']] = result
        
        # Log summary
        success_count = sum(1 for r in results.values() if r['success'])
        logger.info(f"Batch parse complete: {success_count}/{len(file_paths)} successful")
        
        return results


# Convenience function
def parse_resume(file_path: str) -> Dict:
    """
    Convenience function to parse a single resume
    
    Args:
        file_path: Path to resume file
    
    Returns:
        Parse result dict
    """
    parser = ResumeParser()
    return parser.parse(file_path)
