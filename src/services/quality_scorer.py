"""
Resume Quality Scorer

Assesses the quality of resume documents:
- Text extraction quality
- Completeness (has required sections)
- Formatting quality
- Readability metrics
- Scanned document detection
"""

import re
from typing import Dict, Optional
from dataclasses import dataclass
import logging

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

logger = logging.getLogger(__name__)


@dataclass
class QualityScore:
    """Quality assessment scores"""
    overall_score: float  # 0-100
    extraction_quality: float  # 0-100
    completeness: float  # 0-100
    formatting_quality: float  # 0-100
    readability: float  # 0-100
    is_scanned: bool
    has_images: bool
    issues: list
    recommendations: list
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'overall_score': round(self.overall_score, 1),
            'extraction_quality': round(self.extraction_quality, 1),
            'completeness': round(self.completeness, 1),
            'formatting_quality': round(self.formatting_quality, 1),
            'readability': round(self.readability, 1),
            'is_scanned': self.is_scanned,
            'has_images': self.has_images,
            'issues': self.issues,
            'recommendations': self.recommendations
        }


class QualityScorer:
    """Assess resume document quality"""
    
    def __init__(self):
        """Initialize quality scorer"""
        # Expected sections in a resume
        self.expected_sections = [
            'experience', 'work', 'employment',
            'education', 'academic',
            'skills', 'technical', 'competencies',
            'summary', 'objective', 'profile'
        ]
        
        # Minimum text length for quality resume
        self.min_text_length = 200
        self.optimal_text_length = (800, 2500)
    
    def assess_quality(self, pdf_path: str, extracted_text: str) -> QualityScore:
        """
        Assess overall resume quality
        
        Args:
            pdf_path: Path to PDF file
            extracted_text: Extracted text from resume
            
        Returns:
            QualityScore object
        """
        logger.info(f"Assessing quality for: {pdf_path}")
        
        issues = []
        recommendations = []
        
        # 1. Extraction Quality
        extraction_score, is_scanned = self._assess_extraction_quality(
            pdf_path, extracted_text, issues, recommendations
        )
        
        # 2. Completeness
        completeness_score = self._assess_completeness(
            extracted_text, issues, recommendations
        )
        
        # 3. Formatting Quality
        formatting_score = self._assess_formatting(
            pdf_path, extracted_text, issues, recommendations
        )
        
        # 4. Readability
        readability_score = self._assess_readability(
            extracted_text, issues, recommendations
        )
        
        # 5. Check for images
        has_images = self._has_images(pdf_path)
        
        # Calculate overall score (weighted average)
        weights = {
            'extraction': 0.35,
            'completeness': 0.30,
            'formatting': 0.20,
            'readability': 0.15
        }
        
        overall_score = (
            extraction_score * weights['extraction'] +
            completeness_score * weights['completeness'] +
            formatting_score * weights['formatting'] +
            readability_score * weights['readability']
        )
        
        quality = QualityScore(
            overall_score=overall_score,
            extraction_quality=extraction_score,
            completeness=completeness_score,
            formatting_quality=formatting_score,
            readability=readability_score,
            is_scanned=is_scanned,
            has_images=has_images,
            issues=issues,
            recommendations=recommendations
        )
        
        logger.info(f"Overall quality score: {overall_score:.1f}/100")
        
        return quality
    
    def _assess_extraction_quality(
        self,
        pdf_path: str,
        text: str,
        issues: list,
        recommendations: list
    ) -> tuple:
        """Assess text extraction quality"""
        score = 100.0
        is_scanned = False
        
        # Check text length
        if not text or len(text) < self.min_text_length:
            score -= 50
            issues.append("Very little text extracted")
            recommendations.append("Check if document is scanned or image-based")
            is_scanned = True
        
        # Check for gibberish or encoding issues
        non_ascii_ratio = sum(1 for c in text if ord(c) > 127) / max(len(text), 1)
        if non_ascii_ratio > 0.3:
            score -= 20
            issues.append("High non-ASCII character ratio - possible encoding issues")
            recommendations.append("Check document encoding or use OCR")
        
        # Check for excessive whitespace or formatting artifacts
        excessive_spaces = len(re.findall(r'\s{5,}', text))
        if excessive_spaces > 10:
            score -= 10
            issues.append("Excessive whitespace detected")
            recommendations.append("Document may have layout issues")
        
        # Detect if OCR is needed (scanned PDF)
        if fitz and not is_scanned:
            try:
                doc = fitz.open(pdf_path)
                page = doc[0]
                
                # Check if page has images but little text
                image_list = page.get_images()
                page_dict = page.get_text("dict")
                text_blocks = [b for b in page_dict.get("blocks", []) if b.get("type") == 0]
                
                if len(image_list) > 0 and len(text_blocks) < 3:
                    is_scanned = True
                    score -= 30
                    issues.append("Document appears to be scanned")
                    recommendations.append("OCR required for accurate extraction")
                
                doc.close()
            except Exception as e:
                logger.debug(f"Could not analyze PDF structure: {e}")
        
        return max(0, score), is_scanned
    
    def _assess_completeness(
        self,
        text: str,
        issues: list,
        recommendations: list
    ) -> float:
        """Assess completeness of resume sections"""
        score = 100.0
        text_lower = text.lower()
        
        # Check for expected sections
        sections_found = []
        for section in self.expected_sections:
            if section in text_lower:
                sections_found.append(section)
        
        # Group related sections
        has_experience = any(s in sections_found for s in ['experience', 'work', 'employment'])
        has_education = any(s in sections_found for s in ['education', 'academic'])
        has_skills = any(s in sections_found for s in ['skills', 'technical', 'competencies'])
        has_summary = any(s in sections_found for s in ['summary', 'objective', 'profile'])
        
        # Deduct points for missing sections
        if not has_experience:
            score -= 30
            issues.append("Missing work experience section")
            recommendations.append("Add work experience or employment history")
        
        if not has_education:
            score -= 25
            issues.append("Missing education section")
            recommendations.append("Add education background")
        
        if not has_skills:
            score -= 20
            issues.append("Missing skills section")
            recommendations.append("Add skills or technical competencies section")
        
        if not has_summary:
            score -= 10
            issues.append("Missing professional summary")
            recommendations.append("Consider adding a professional summary")
        
        # Check for contact information
        has_email = bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text))
        has_phone = bool(re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text))
        
        if not has_email:
            score -= 10
            issues.append("No email address found")
            recommendations.append("Add email contact information")
        
        if not has_phone:
            score -= 5
            issues.append("No phone number found")
            recommendations.append("Add phone contact information")
        
        return max(0, score)
    
    def _assess_formatting(
        self,
        pdf_path: str,
        text: str,
        issues: list,
        recommendations: list
    ) -> float:
        """Assess formatting quality"""
        score = 100.0
        
        # Check text length (not too short, not too long)
        text_length = len(text)
        if text_length < self.optimal_text_length[0]:
            score -= 15
            issues.append("Resume is too brief")
            recommendations.append("Expand content with more details")
        elif text_length > self.optimal_text_length[1]:
            score -= 10
            issues.append("Resume is too lengthy")
            recommendations.append("Consider condensing to 1-2 pages")
        
        # Check for bullet points (indicates good formatting)
        bullet_chars = ['•', '-', '*', '○', '●']
        has_bullets = any(char in text for char in bullet_chars)
        if not has_bullets:
            score -= 15
            issues.append("No bullet points found")
            recommendations.append("Use bullet points for better readability")
        
        # Check for consistent capitalization
        all_caps_lines = len(re.findall(r'^[A-Z\s]{10,}$', text, re.MULTILINE))
        if all_caps_lines > 10:
            score -= 10
            issues.append("Excessive use of ALL CAPS")
            recommendations.append("Use title case for better readability")
        
        return max(0, score)
    
    def _assess_readability(
        self,
        text: str,
        issues: list,
        recommendations: list
    ) -> float:
        """Assess readability of text"""
        score = 100.0
        
        if not text:
            return 0
        
        # Calculate basic readability metrics
        words = text.split()
        num_words = len(words)
        
        if num_words == 0:
            return 0
        
        # Average word length
        avg_word_length = sum(len(word) for word in words) / num_words
        
        if avg_word_length > 8:
            score -= 10
            issues.append("Complex vocabulary detected")
            recommendations.append("Use simpler, more direct language")
        
        # Check for very long paragraphs (poor readability)
        paragraphs = text.split('\n\n')
        long_paragraphs = [p for p in paragraphs if len(p) > 500]
        if len(long_paragraphs) > 3:
            score -= 15
            issues.append("Large blocks of text without breaks")
            recommendations.append("Break up text into smaller paragraphs")
        
        # Check for grammar issues (basic checks)
        # Multiple consecutive spaces
        if re.search(r'\s{3,}', text):
            score -= 5
            issues.append("Inconsistent spacing")
        
        # Missing punctuation at sentence ends
        sentences = re.split(r'[.!?]\s+', text)
        if len(sentences) < num_words / 20:  # Very few sentences for word count
            score -= 10
            issues.append("Run-on text without proper punctuation")
        
        return max(0, score)
    
    def _has_images(self, pdf_path: str) -> bool:
        """Check if PDF contains images"""
        if not fitz:
            return False
        
        try:
            doc = fitz.open(pdf_path)
            has_imgs = False
            
            for page in doc:
                if len(page.get_images()) > 0:
                    has_imgs = True
                    break
            
            doc.close()
            return has_imgs
        except Exception as e:
            logger.debug(f"Could not check for images: {e}")
            return False


# Convenience function
def assess_quality(pdf_path: str, extracted_text: str) -> QualityScore:
    """
    Assess resume quality
    
    Args:
        pdf_path: Path to PDF file
        extracted_text: Extracted text
        
    Returns:
        QualityScore object
    """
    scorer = QualityScorer()
    return scorer.assess_quality(pdf_path, extracted_text)
