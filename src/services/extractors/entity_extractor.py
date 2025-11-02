"""
Entity Extractor Service - Extract named entities using spaCy NER
Extracts organizations, locations, dates, and custom resume entities
"""

import re
import logging
from typing import Dict, List, Optional, Set
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Try to import spacy
try:
    import spacy
    from spacy.matcher import Matcher
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logger.warning("spaCy not installed. Entity extraction will be limited.")


@dataclass
class Entity:
    """Represents an extracted entity"""
    text: str
    label: str
    start: int
    end: int
    confidence: float = 1.0


class EntityExtractor:
    """
    Extract named entities from resume text using spaCy NER
    """
    
    def __init__(self, model_name: str = "en_core_web_md"):
        """
        Initialize Entity Extractor
        
        Args:
            model_name: spaCy model to use (default: en_core_web_md)
        """
        self.nlp = None
        self.matcher = None
        self.spacy_available = SPACY_AVAILABLE
        
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load(model_name)
                self.matcher = Matcher(self.nlp.vocab)
                self._add_custom_patterns()
                logger.info(f"Loaded spaCy model: {model_name}")
            except OSError:
                logger.error(
                    f"Could not load spaCy model '{model_name}'. "
                    f"Install with: python -m spacy download {model_name}"
                )
                self.spacy_available = False
        
        if not self.spacy_available:
            logger.warning("Entity extraction will use fallback regex patterns")
    
    def _add_custom_patterns(self):
        """Add custom entity patterns for resume-specific terms"""
        if not self.matcher:
            return
        
        # Degree patterns
        degree_patterns = [
            [{"LOWER": {"IN": ["bachelor", "bachelors", "b.s.", "b.a.", "bs", "ba"]}}],
            [{"LOWER": {"IN": ["master", "masters", "m.s.", "m.a.", "ms", "ma"]}}],
            [{"LOWER": {"IN": ["phd", "ph.d.", "doctorate"]}}],
            [{"LOWER": "mba"}],
        ]
        self.matcher.add("DEGREE", degree_patterns)
        
        # Programming language patterns
        prog_lang_patterns = [
            [{"LOWER": {"IN": ["python", "java", "javascript", "c++", "ruby", "go", "rust", "kotlin"]}}],
        ]
        self.matcher.add("PROG_LANG", prog_lang_patterns)
    
    def extract_entities(self, text: str) -> Dict[str, List[Entity]]:
        """
        Extract all named entities from text
        
        Args:
            text: Text to extract entities from
            
        Returns:
            Dictionary of entity_type -> List[Entity]
        """
        if not self.spacy_available or not self.nlp:
            return self._extract_entities_fallback(text)
        
        try:
            doc = self.nlp(text)
            
            entities = {
                'persons': [],
                'organizations': [],
                'locations': [],
                'dates': [],
                'degrees': [],
                'skills': [],
            }
            
            # Extract spaCy NER entities
            for ent in doc.ents:
                entity = Entity(
                    text=ent.text,
                    label=ent.label_,
                    start=ent.start_char,
                    end=ent.end_char
                )
                
                if ent.label_ == 'PERSON':
                    entities['persons'].append(entity)
                elif ent.label_ == 'ORG':
                    entities['organizations'].append(entity)
                elif ent.label_ in ['GPE', 'LOC']:
                    entities['locations'].append(entity)
                elif ent.label_ == 'DATE':
                    entities['dates'].append(entity)
            
            # Extract custom pattern matches
            matches = self.matcher(doc)
            for match_id, start, end in matches:
                span = doc[start:end]
                match_label = self.nlp.vocab.strings[match_id]
                
                entity = Entity(
                    text=span.text,
                    label=match_label,
                    start=span.start_char,
                    end=span.end_char
                )
                
                if match_label == 'DEGREE':
                    entities['degrees'].append(entity)
                elif match_label == 'PROG_LANG':
                    entities['skills'].append(entity)
            
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting entities with spaCy: {e}")
            return self._extract_entities_fallback(text)
    
    def _extract_entities_fallback(self, text: str) -> Dict[str, List[Entity]]:
        """
        Fallback entity extraction using regex (when spaCy unavailable)
        
        Args:
            text: Text to extract from
            
        Returns:
            Dictionary of entity_type -> List[Entity]
        """
        entities = {
            'persons': [],
            'organizations': [],
            'locations': [],
            'dates': [],
            'degrees': [],
            'skills': [],
        }
        
        # Extract dates
        date_patterns = [
            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b',
            r'\b\d{1,2}/\d{4}\b',
            r'\b(19|20)\d{2}\b',
        ]
        
        for pattern in date_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities['dates'].append(Entity(
                    text=match.group(),
                    label='DATE',
                    start=match.start(),
                    end=match.end()
                ))
        
        # Extract degrees
        degree_pattern = r'\b(Bachelor|Master|PhD|MBA|B\.?S\.?|M\.?S\.?|B\.?A\.?|M\.?A\.?)\b'
        for match in re.finditer(degree_pattern, text, re.IGNORECASE):
            entities['degrees'].append(Entity(
                text=match.group(),
                label='DEGREE',
                start=match.start(),
                end=match.end()
            ))
        
        return entities
    
    def extract_organizations(self, text: str) -> List[str]:
        """
        Extract organization/company names from text
        
        Args:
            text: Text to extract from
            
        Returns:
            List of organization names
        """
        entities = self.extract_entities(text)
        return list(set([ent.text for ent in entities['organizations']]))
    
    def extract_locations(self, text: str) -> List[str]:
        """
        Extract location names from text
        
        Args:
            text: Text to extract from
            
        Returns:
            List of location names
        """
        entities = self.extract_entities(text)
        return list(set([ent.text for ent in entities['locations']]))
    
    def extract_dates(self, text: str) -> List[str]:
        """
        Extract date mentions from text
        
        Args:
            text: Text to extract from
            
        Returns:
            List of date strings
        """
        entities = self.extract_entities(text)
        return list(set([ent.text for ent in entities['dates']]))
    
    def extract_persons(self, text: str) -> List[str]:
        """
        Extract person names from text
        
        Args:
            text: Text to extract from
            
        Returns:
            List of person names
        """
        entities = self.extract_entities(text)
        return list(set([ent.text for ent in entities['persons']]))
    
    def extract_from_section(self, section_text: str, section_type: str) -> Dict[str, List[str]]:
        """
        Extract entities from a specific resume section with context
        
        Args:
            section_text: Text of the section
            section_type: Type of section (experience, education, etc.)
            
        Returns:
            Dictionary of extracted entities by type
        """
        entities = self.extract_entities(section_text)
        
        result = {
            'organizations': [ent.text for ent in entities['organizations']],
            'locations': [ent.text for ent in entities['locations']],
            'dates': [ent.text for ent in entities['dates']],
        }
        
        # Add section-specific extractions
        if section_type == 'education':
            result['degrees'] = [ent.text for ent in entities['degrees']]
        
        return result


def test_entity_extractor():
    """Test entity extractor"""
    extractor = EntityExtractor()
    
    if not extractor.spacy_available:
        print("❌ spaCy not available. Testing fallback mode...")
    else:
        print("✅ spaCy loaded successfully!")
    
    # Test text
    test_text = """
    John Smith worked at Google from January 2020 to December 2023.
    He has a Master of Science degree from MIT in Cambridge, Massachusetts.
    He knows Python, Java, and Machine Learning.
    """
    
    print("\n" + "="*60)
    print("Test Text:")
    print("="*60)
    print(test_text)
    
    print("\n" + "="*60)
    print("Extracted Entities:")
    print("="*60)
    
    entities = extractor.extract_entities(test_text)
    
    for entity_type, entity_list in entities.items():
        if entity_list:
            print(f"\n{entity_type.upper()}:")
            for ent in entity_list:
                print(f"  - {ent.text} ({ent.label})")
    
    print("\n" + "="*60)
    print("Specific Extractions:")
    print("="*60)
    
    print(f"\nOrganizations: {extractor.extract_organizations(test_text)}")
    print(f"Locations: {extractor.extract_locations(test_text)}")
    print(f"Dates: {extractor.extract_dates(test_text)}")
    print(f"Persons: {extractor.extract_persons(test_text)}")


if __name__ == "__main__":
    test_entity_extractor()
