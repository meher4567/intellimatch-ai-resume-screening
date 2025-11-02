"""
NER-Based Entity Extractor for Resumes
Uses spaCy's NER to extract entities with ML
"""

import spacy
from typing import Dict, List, Optional, Set, Tuple
import logging
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)


@dataclass
class ExtractedEntity:
    """Represents an extracted entity with confidence"""
    text: str
    label: str
    confidence: float
    start: int
    end: int


class NERExtractor:
    """
    ML-based entity extractor using spaCy NER
    Extracts: PERSON names, ORG (companies), GPE (locations), DATE, etc.
    """
    
    def __init__(self, model_name: str = "en_core_web_md"):
        """
        Initialize NER extractor
        
        Args:
            model_name: spaCy model to use (en_core_web_md recommended)
        """
        try:
            self.nlp = spacy.load(model_name)
            logger.info(f"Loaded spaCy model: {model_name}")
        except OSError:
            logger.error(f"Model {model_name} not found. Run: python -m spacy download {model_name}")
            raise
        
        # Cache for processed documents
        self._cache = {}
    
    def extract_names(self, text: str, top_n: int = 3) -> List[ExtractedEntity]:
        """
        Extract person names using NER
        
        Args:
            text: Resume text
            top_n: Maximum number of names to return
            
        Returns:
            List of ExtractedEntity objects for PERSON entities
        """
        doc = self._get_or_process(text)
        
        # Extract PERSON entities
        person_entities = []
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                # Clean the entity text (remove newlines, URLs, etc.)
                cleaned_text = self._clean_entity_text(ent.text)
                
                # Skip if cleaning removed everything or left junk
                if not cleaned_text or len(cleaned_text) < 2:
                    continue
                
                # Skip if doesn't look like a name
                if not self._looks_like_name(cleaned_text):
                    continue
                
                # Calculate confidence based on position and context
                confidence = self._calculate_name_confidence(ent, doc, cleaned_text)
                
                person_entities.append(ExtractedEntity(
                    text=cleaned_text,
                    label="PERSON",
                    confidence=confidence,
                    start=ent.start_char,
                    end=ent.end_char
                ))
        
        # Sort by confidence and position (earlier in document = higher confidence)
        person_entities.sort(key=lambda x: (x.confidence, -x.start), reverse=True)
        
        return person_entities[:top_n]
    
    def extract_organizations(self, text: str, min_confidence: float = 0.5) -> List[ExtractedEntity]:
        """
        Extract organization/company names using NER
        
        Args:
            text: Resume text
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of ExtractedEntity objects for ORG entities
        """
        doc = self._get_or_process(text)
        
        organizations = []
        for ent in doc.ents:
            if ent.label_ == "ORG":
                # Calculate confidence
                confidence = self._calculate_org_confidence(ent, doc)
                
                if confidence >= min_confidence:
                    organizations.append(ExtractedEntity(
                        text=ent.text,
                        label="ORG",
                        confidence=confidence,
                        start=ent.start_char,
                        end=ent.end_char
                    ))
        
        # Remove duplicates, keep highest confidence
        seen = {}
        for org in organizations:
            normalized = org.text.lower().strip()
            if normalized not in seen or org.confidence > seen[normalized].confidence:
                seen[normalized] = org
        
        return list(seen.values())
    
    def extract_locations(self, text: str, min_confidence: float = 0.5) -> List[ExtractedEntity]:
        """
        Extract geographic locations using NER
        
        Args:
            text: Resume text
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of ExtractedEntity objects for GPE entities
        """
        doc = self._get_or_process(text)
        
        locations = []
        for ent in doc.ents:
            if ent.label_ == "GPE":  # Geopolitical Entity
                confidence = self._calculate_location_confidence(ent, doc)
                
                if confidence >= min_confidence:
                    locations.append(ExtractedEntity(
                        text=ent.text,
                        label="GPE",
                        confidence=confidence,
                        start=ent.start_char,
                        end=ent.end_char
                    ))
        
        return locations
    
    def extract_dates(self, text: str) -> List[ExtractedEntity]:
        """
        Extract dates using NER
        
        Args:
            text: Resume text
            
        Returns:
            List of ExtractedEntity objects for DATE entities
        """
        doc = self._get_or_process(text)
        
        dates = []
        for ent in doc.ents:
            if ent.label_ == "DATE":
                dates.append(ExtractedEntity(
                    text=ent.text,
                    label="DATE",
                    confidence=0.9,  # spaCy dates are usually reliable
                    start=ent.start_char,
                    end=ent.end_char
                ))
        
        return dates
    
    def extract_all_entities(self, text: str) -> Dict[str, List[ExtractedEntity]]:
        """
        Extract all relevant entities from resume
        
        Args:
            text: Resume text
            
        Returns:
            Dictionary mapping entity type to list of extracted entities
        """
        doc = self._get_or_process(text)
        
        entities = {
            'PERSON': [],
            'ORG': [],
            'GPE': [],
            'DATE': [],
            'MONEY': [],
            'PERCENT': [],
            'CARDINAL': [],
        }
        
        for ent in doc.ents:
            if ent.label_ in entities:
                confidence = self._calculate_entity_confidence(ent, doc)
                entities[ent.label_].append(ExtractedEntity(
                    text=ent.text,
                    label=ent.label_,
                    confidence=confidence,
                    start=ent.start_char,
                    end=ent.end_char
                ))
        
        return entities
    
    def _get_or_process(self, text: str):
        """Get cached doc or process new text"""
        text_hash = hash(text)
        if text_hash not in self._cache:
            self._cache[text_hash] = self.nlp(text)
        return self._cache[text_hash]
    
    def _clean_entity_text(self, text: str) -> str:
        """
        Clean entity text by removing URLs, newlines, extra spaces
        """
        # Remove URLs
        text = re.sub(r'https?://\S+', '', text)
        text = re.sub(r'www\.\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Replace newlines with spaces
        text = text.replace('\n', ' ').replace('\r', ' ')
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove leading/trailing punctuation
        text = text.strip('.,;:!?-_/\\|')
        
        return text.strip()
    
    def _looks_like_name(self, text: str) -> bool:
        """
        Check if text looks like a person's name
        """
        # Must have at least one letter
        if not re.search(r'[a-zA-Z]', text):
            return False
        
        # Must not be all uppercase unless it's a short name
        if text.isupper() and len(text) > 15:
            return False
        
        # Should have 1-4 words (typical name length)
        words = text.split()
        if len(words) == 0 or len(words) > 5:
            return False
        
        # Each word should start with capital letter (mostly)
        capital_count = sum(1 for w in words if w and w[0].isupper())
        if capital_count < len(words) * 0.5:  # At least 50% capitalized
            return False
        
        # Should not contain weird characters
        if re.search(r'[<>{}[\]@#$%^&*+=|\\]', text):
            return False
        
        # Should not be too short
        if len(text) < 3:
            return False
        
        return True
    
    def _calculate_name_confidence(self, ent, doc, cleaned_text: str) -> float:
        """
        Calculate confidence score for a PERSON entity
        Higher confidence if:
        - Appears near beginning of document
        - Capitalized properly
        - Appears in context of contact information
        """
        confidence = 0.7  # Base confidence from NER
        
        # Bonus for appearing early in document (first 20% of text)
        if ent.start_char < len(doc.text) * 0.2:
            confidence += 0.2
        
        # Bonus for proper capitalization
        if cleaned_text.istitle():
            confidence += 0.05
        
        # Bonus for appearing near contact keywords
        context = doc.text[max(0, ent.start_char-100):min(len(doc.text), ent.end_char+100)].lower()
        contact_keywords = ['email', 'phone', 'linkedin', 'github', 'contact']
        if any(keyword in context for keyword in contact_keywords):
            confidence += 0.1
        
        # Penalty for very long names (likely not a person)
        if len(cleaned_text.split()) > 4:
            confidence -= 0.2
        
        # Bonus for having first and last name (2-3 words is ideal)
        word_count = len(cleaned_text.split())
        if word_count in [2, 3]:
            confidence += 0.1
        
        return min(1.0, max(0.0, confidence))
    
    def _calculate_org_confidence(self, ent, doc) -> float:
        """
        Calculate confidence score for an ORG entity
        """
        confidence = 0.6  # Base confidence
        
        # Bonus for appearing near work experience keywords
        context = doc.text[max(0, ent.start_char-150):min(len(doc.text), ent.end_char+150)].lower()
        work_keywords = ['experience', 'work', 'employment', 'intern', 'company', 'corporation', 'inc', 'ltd']
        if any(keyword in context for keyword in work_keywords):
            confidence += 0.3
        
        # Bonus for containing corporate suffixes
        corporate_suffixes = ['Inc', 'LLC', 'Ltd', 'Corporation', 'Corp', 'Co', 'Technologies', 'Labs', 'Systems']
        if any(suffix in ent.text for suffix in corporate_suffixes):
            confidence += 0.2
        
        # Penalty for single word orgs (less reliable)
        if len(ent.text.split()) == 1:
            confidence -= 0.1
        
        return min(1.0, max(0.0, confidence))
    
    def _calculate_location_confidence(self, ent, doc) -> float:
        """Calculate confidence score for GPE entity"""
        confidence = 0.7
        
        # Bonus for appearing near location keywords
        context = doc.text[max(0, ent.start_char-100):min(len(doc.text), ent.end_char+100)].lower()
        location_keywords = ['location', 'address', 'based', 'city', 'state', 'country']
        if any(keyword in context for keyword in location_keywords):
            confidence += 0.2
        
        return min(1.0, confidence)
    
    def _calculate_entity_confidence(self, ent, doc) -> float:
        """Generic confidence calculator"""
        if ent.label_ == "PERSON":
            return self._calculate_name_confidence(ent, doc)
        elif ent.label_ == "ORG":
            return self._calculate_org_confidence(ent, doc)
        elif ent.label_ == "GPE":
            return self._calculate_location_confidence(ent, doc)
        else:
            return 0.7  # Default confidence for other entities
    
    def clear_cache(self):
        """Clear the document cache"""
        self._cache.clear()


def get_best_name_from_entities(entities: List[ExtractedEntity]) -> Optional[str]:
    """
    Helper function to get the most likely name from extracted entities
    
    Args:
        entities: List of PERSON entities
        
    Returns:
        Best name guess or None
    """
    if not entities:
        return None
    
    # Return highest confidence entity
    best = max(entities, key=lambda x: x.confidence)
    return best.text if best.confidence > 0.5 else None
