"""
Simple wrapper for the trained experience classifier
Uses transformers pipeline with proper label mapping
"""
from transformers import pipeline
import json
from pathlib import Path
from typing import Dict, Any, List

class TrainedExperienceClassifier:
    """Wrapper for trained BERT experience classifier"""
    
    # Label mapping (from training)
    LABEL_MAP = {
        'LABEL_0': 'entry',
        'LABEL_1': 'mid',
        'LABEL_2': 'senior',
        'LABEL_3': 'expert'
    }
    
    REVERSE_MAP = {
        'entry': 'LABEL_0',
        'mid': 'LABEL_1',
        'senior': 'LABEL_2',
        'expert': 'LABEL_3'
    }
    
    def __init__(self, model_path: str = "models/experience_classifier"):
        """Initialize classifier"""
        self.model_path = model_path
        self.classifier = None
        self._load_model()
    
    def _load_model(self):
        """Load the trained model"""
        model_path = Path(self.model_path)
        
        if not model_path.exists():
            raise FileNotFoundError(
                f"Trained model not found at: {model_path}\n"
                "Please run the training notebook first!"
            )
        
        print(f"📥 Loading trained experience classifier from: {model_path}")
        
        try:
            self.classifier = pipeline(
                "text-classification",
                model=str(model_path),
                device=-1  # Use CPU (change to 0 for GPU)
            )
            print("✅ Model loaded successfully!")
        except Exception as e:
            raise RuntimeError(f"Failed to load model: {e}")
    
    def predict(self, text: str) -> Dict[str, Any]:
        """
        Predict experience level from text
        
        Args:
            text: Resume text or work experience description
            
        Returns:
            {
                'level': str,  # 'entry', 'mid', 'senior', or 'expert'
                'confidence': float,  # 0-1 confidence score
                'raw_label': str  # Original LABEL_X from model
            }
        """
        if not text or not text.strip():
            return {
                'level': 'entry',
                'confidence': 0.5,
                'raw_label': 'LABEL_0'
            }
        
        # Truncate text to BERT limit
        text = text[:512]
        
        # Get prediction
        result = self.classifier(text)[0]
        raw_label = result['label']
        confidence = result['score']
        
        # Map to readable level
        level = self.LABEL_MAP.get(raw_label, 'entry')
        
        return {
            'level': level,
            'confidence': confidence,
            'raw_label': raw_label
        }
    
    def predict_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Predict for multiple texts"""
        return [self.predict(text) for text in texts]
    
    def classify(self, candidate_data: Dict, **kwargs) -> Dict[str, Any]:
        """
        Classify experience level from candidate data
        Compatible with existing classifier interface
        
        Args:
            candidate_data: Dict with 'experience' and other resume fields
            
        Returns:
            {
                'level': str,
                'confidence': float
            }
        """
        # Extract text from candidate data
        text_parts = []
        
        # Get experience entries
        for exp in candidate_data.get('experience', []):
            title = exp.get('title', '')
            company = exp.get('company', '')
            responsibilities = ' '.join(exp.get('responsibilities', []))
            
            text_parts.append(f"{title} at {company}. {responsibilities}")
        
        # Get skills
        skills = candidate_data.get('skills', [])
        if skills:
            text_parts.append(f"Skills: {', '.join(skills[:20])}")
        
        # Combine text
        text = ' '.join(text_parts)
        
        if not text.strip():
            return {'level': 'entry', 'confidence': 0.5}
        
        # Predict
        result = self.predict(text)
        
        return {
            'level': result['level'],
            'confidence': result['confidence']
        }


# Convenience function
def load_trained_classifier(model_path: str = "models/experience_classifier"):
    """Load the trained experience classifier"""
    return TrainedExperienceClassifier(model_path)


if __name__ == "__main__":
    # Test the classifier
    print("=" * 70)
    print("🧪 Testing Trained Experience Classifier Wrapper")
    print("=" * 70)
    
    try:
        classifier = TrainedExperienceClassifier()
        
        test_cases = [
            "Senior Software Engineer with 8 years of experience in Python and cloud technologies",
            "Recent graduate with internship experience. Entry level position",
            "Principal Architect with 15 years building enterprise systems",
            "Software Engineer with 3 years developing web applications"
        ]
        
        print("\n🧪 Test Cases:\n")
        for i, text in enumerate(test_cases, 1):
            result = classifier.predict(text)
            print(f"{i}. {text[:60]}...")
            print(f"   Level: {result['level'].upper()}")
            print(f"   Confidence: {result['confidence']*100:.2f}%\n")
        
        print("✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
