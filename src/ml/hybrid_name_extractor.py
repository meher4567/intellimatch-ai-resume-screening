"""
Hybrid Name Extractor
Combines ML-based NER with rule-based patterns for maximum accuracy
"""

from typing import Optional
import logging
from .ner_extractor import NERExtractor, get_best_name_from_entities
from ..services.name_extractor import NameExtractor

logger = logging.getLogger(__name__)


class HybridNameExtractor:
    """
    Hybrid name extractor that combines ML (spaCy NER) with rule-based extraction
    
    Strategy:
    1. Try ML-based NER first (fast, handles variations)
    2. Fall back to rule-based if ML confidence is low
    3. Prefer rules for simple cases (they're very accurate)
    4. Use ML for complex cases (unusual formats, nicknames)
    """
    
    def __init__(self, ml_confidence_threshold: float = 0.85):
        """
        Initialize hybrid extractor
        
        Args:
            ml_confidence_threshold: Minimum confidence to trust ML over rules
        """
        self.ner_extractor = NERExtractor()
        self.rule_extractor = NameExtractor()
        self.ml_threshold = ml_confidence_threshold
        
        logger.info(f"Initialized HybridNameExtractor (ML threshold: {ml_confidence_threshold})")
    
    def extract_name(self, text: str, prefer_ml: bool = False) -> Optional[str]:
        """
        Extract name using hybrid approach
        
        Args:
            text: Resume text
            prefer_ml: If True, prefer ML over rules (default: False)
            
        Returns:
            Extracted name or None
        """
        # Get both results
        ml_entities = self.ner_extractor.extract_names(text, top_n=1)
        ml_name = get_best_name_from_entities(ml_entities)
        ml_confidence = ml_entities[0].confidence if ml_entities else 0.0
        
        rule_name = self.rule_extractor.extract_name(text)
        
        # Decision logic
        if prefer_ml:
            # User explicitly wants ML
            if ml_name and ml_confidence > 0.5:
                logger.info(f"Using ML name (prefer_ml=True): {ml_name} (conf: {ml_confidence:.2f})")
                return ml_name
            elif rule_name:
                logger.info(f"ML failed, using rule-based: {rule_name}")
                return rule_name
            elif ml_name:
                logger.warning(f"Both ML and rules uncertain, using ML: {ml_name}")
                return ml_name
            else:
                return None
        else:
            # Default strategy: Rules first (they're very accurate for names)
            if rule_name:
                # Rules found something
                if ml_name and ml_confidence > self.ml_threshold:
                    # ML has high confidence - compare results
                    if self._names_match(ml_name, rule_name):
                        logger.info(f"ML and rules agree: {rule_name}")
                        return rule_name
                    else:
                        # They disagree - trust rules for names
                        logger.warning(f"ML vs Rules differ. ML: {ml_name}, Rule: {rule_name}. Using rules.")
                        return rule_name
                else:
                    # ML has low confidence or no result - use rules
                    logger.info(f"Using rule-based name: {rule_name}")
                    return rule_name
            else:
                # Rules failed - try ML
                if ml_name:
                    logger.info(f"Rules failed, using ML name: {ml_name} (conf: {ml_confidence:.2f})")
                    return ml_name
                else:
                    logger.warning("Both ML and rules failed to extract name")
                    return None
    
    def extract_with_details(self, text: str) -> dict:
        """
        Extract name with detailed information about the extraction
        
        Returns:
            Dict with:
                - name: Final extracted name
                - method: How it was extracted ('ml', 'rules', 'both_agree', 'failed')
                - ml_name: What ML extracted
                - ml_confidence: ML confidence score
                - rule_name: What rules extracted
                - all_ml_candidates: All ML candidates found
        """
        ml_entities = self.ner_extractor.extract_names(text, top_n=3)
        ml_name = get_best_name_from_entities(ml_entities)
        ml_confidence = ml_entities[0].confidence if ml_entities else 0.0
        
        rule_name = self.rule_extractor.extract_name(text)
        
        # Determine final name and method
        if rule_name and ml_name and self._names_match(ml_name, rule_name):
            final_name = rule_name
            method = 'both_agree'
        elif rule_name:
            final_name = rule_name
            method = 'rules'
        elif ml_name:
            final_name = ml_name
            method = 'ml'
        else:
            final_name = None
            method = 'failed'
        
        return {
            'name': final_name,
            'method': method,
            'ml_name': ml_name,
            'ml_confidence': ml_confidence,
            'rule_name': rule_name,
            'all_ml_candidates': [{'text': e.text, 'confidence': e.confidence} for e in ml_entities]
        }
    
    def _names_match(self, name1: str, name2: str) -> bool:
        """
        Check if two names are the same (case-insensitive, ignoring punctuation)
        """
        if not name1 or not name2:
            return False
        
        # Normalize for comparison
        n1 = name1.lower().replace('.', '').replace(',', '').strip()
        n2 = name2.lower().replace('.', '').replace(',', '').strip()
        
        return n1 == n2


# Convenience function for backward compatibility
def extract_name_hybrid(text: str) -> Optional[str]:
    """
    Extract name using hybrid approach
    Simple interface for quick usage
    """
    extractor = HybridNameExtractor()
    return extractor.extract_name(text)
