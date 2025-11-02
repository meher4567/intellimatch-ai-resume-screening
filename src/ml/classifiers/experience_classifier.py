"""
Experience Level Classifier
BERT-based classifier to determine candidate experience level:
- Entry Level (0-2 years)
- Mid Level (2-5 years)
- Senior Level (5-8 years)
- Expert/Lead (8+ years)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import torch
import torch.nn as nn
from torch.optim import AdamW
from transformers import BertTokenizer, BertModel, get_linear_schedule_with_warmup
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
from dataclasses import dataclass
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExperienceFeatures:
    """Features extracted from resume for classification"""
    years: float  # Total years of experience
    job_titles: List[str]  # All job titles
    responsibilities: List[str]  # Key responsibilities
    achievements: List[str]  # Achievements/accomplishments
    latest_title: str  # Most recent job title
    skills_count: int  # Number of skills
    education_level: str  # Highest degree


class ExperienceLevelClassifier:
    """
    BERT-based classifier for experience level detection
    
    Classifies candidates into:
    - entry: 0-2 years (Junior, Associate, Intern)
    - mid: 2-5 years (Software Engineer, Analyst)
    - senior: 5-8 years (Senior Engineer, Tech Lead)
    - expert: 8+ years (Principal, Architect, Director)
    """
    
    # Experience level definitions
    LEVELS = ['entry', 'mid', 'senior', 'expert']
    
    # Keywords for each level (for rule-based fallback)
    LEVEL_KEYWORDS = {
        'entry': ['junior', 'jr', 'associate', 'intern', 'graduate', 'trainee', 'entry'],
        'mid': ['engineer', 'developer', 'analyst', 'consultant', 'specialist'],
        'senior': ['senior', 'sr', 'lead', 'staff'],
        'expert': ['principal', 'architect', 'director', 'vp', 'chief', 'head of', 'fellow', 'distinguished']
    }
    
    def __init__(self,
                 model_name: str = 'bert-base-uncased',
                 device: Optional[str] = None,
                 use_pretrained: bool = False,
                 model_path: Optional[str] = None):
        """
        Initialize experience classifier
        
        Args:
            model_name: Pre-trained BERT model name
            device: Device to use ('cuda', 'cpu', or None for auto)
            use_pretrained: Load pre-trained classifier weights
            model_path: Path to saved model weights
        """
        self.model_name = model_name
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.num_labels = len(self.LEVELS)
        
        # Initialize tokenizer
        print(f"🔧 Loading tokenizer: {model_name}")
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        
        # Build model
        print(f"🏗️  Building classifier model...")
        self.model = self._build_model()
        self.model.to(self.device)
        
        # Load pre-trained weights if specified
        if use_pretrained and model_path:
            self.load_model(model_path)
        
        # Training history
        self.training_history = {
            'train_loss': [],
            'val_loss': [],
            'val_accuracy': []
        }
        
        print(f"✅ Experience Classifier ready!")
        print(f"   Model: {model_name}")
        print(f"   Device: {self.device}")
        print(f"   Levels: {', '.join(self.LEVELS)}")
    
    def _build_model(self) -> nn.Module:
        """Build BERT classification model"""
        
        class BertExperienceClassifier(nn.Module):
            """BERT model with classification head"""
            
            def __init__(self, bert_model_name: str, num_labels: int):
                super().__init__()
                self.bert = BertModel.from_pretrained(bert_model_name)
                self.dropout = nn.Dropout(0.3)
                self.classifier = nn.Linear(self.bert.config.hidden_size, num_labels)
            
            def forward(self, input_ids, attention_mask):
                outputs = self.bert(
                    input_ids=input_ids,
                    attention_mask=attention_mask
                )
                # Use [CLS] token representation
                pooled_output = outputs.pooler_output
                pooled_output = self.dropout(pooled_output)
                logits = self.classifier(pooled_output)
                return logits
        
        return BertExperienceClassifier(self.model_name, self.num_labels)
    
    def _prepare_text(self, features: ExperienceFeatures) -> str:
        """
        Prepare text input from features
        
        Combines job titles, responsibilities, and context into a single text
        """
        parts = []
        
        # Add years context
        parts.append(f"{features.years:.1f} years of experience")
        
        # Add latest title
        if features.latest_title:
            parts.append(f"Current: {features.latest_title}")
        
        # Add all titles
        if features.job_titles:
            titles_str = ". ".join(features.job_titles[:3])  # Top 3 titles
            parts.append(f"Titles: {titles_str}")
        
        # Add key responsibilities (sample)
        if features.responsibilities:
            resp_str = ". ".join(features.responsibilities[:3])
            parts.append(f"Responsibilities: {resp_str}")
        
        # Add achievements (sample)
        if features.achievements:
            ach_str = ". ".join(features.achievements[:2])
            parts.append(f"Achievements: {ach_str}")
        
        # Add skills count context
        parts.append(f"{features.skills_count} skills")
        
        # Add education
        if features.education_level:
            parts.append(f"Education: {features.education_level}")
        
        return ". ".join(parts)
    
    def _tokenize(self, text: str, max_length: int = 256) -> Dict[str, torch.Tensor]:
        """Tokenize text for BERT"""
        encoding = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=max_length,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].to(self.device),
            'attention_mask': encoding['attention_mask'].to(self.device)
        }
    
    def classify(self,
                resume_data: Dict[str, Any],
                use_hybrid: bool = True,
                confidence_threshold: float = 0.7) -> Dict[str, Any]:
        """
        Classify experience level from resume data
        
        Args:
            resume_data: Parsed resume data
            use_hybrid: Use hybrid approach (ML + rule-based)
            confidence_threshold: Minimum confidence for ML prediction
            
        Returns:
            Dict with predicted level, confidence, and reasoning
        """
        # Extract features
        features = self._extract_features(resume_data)
        
        # Get ML prediction
        ml_prediction = self._predict_ml(features)
        
        # If hybrid mode and low confidence, use rule-based fallback
        if use_hybrid and ml_prediction['confidence'] < confidence_threshold:
            rule_prediction = self._predict_rule_based(features)
            
            return {
                'level': rule_prediction['level'],
                'confidence': rule_prediction['confidence'],
                'method': 'hybrid',
                'ml_prediction': ml_prediction,
                'rule_prediction': rule_prediction,
                'reasoning': self._generate_reasoning(features, rule_prediction['level'])
            }
        
        return {
            'level': ml_prediction['level'],
            'confidence': ml_prediction['confidence'],
            'method': 'ml',
            'ml_prediction': ml_prediction,
            'reasoning': self._generate_reasoning(features, ml_prediction['level'])
        }
    
    def _predict_ml(self, features: ExperienceFeatures) -> Dict[str, Any]:
        """ML-based prediction using BERT"""
        self.model.eval()
        
        # Prepare text
        text = self._prepare_text(features)
        
        # Tokenize
        inputs = self._tokenize(text)
        
        # Predict
        with torch.no_grad():
            logits = self.model(
                input_ids=inputs['input_ids'],
                attention_mask=inputs['attention_mask']
            )
            
            # Get probabilities
            probs = torch.softmax(logits, dim=1)
            confidence, pred_idx = torch.max(probs, dim=1)
            
            predicted_level = self.LEVELS[pred_idx.item()]
            confidence_score = confidence.item()
            
            # Get all class probabilities
            all_probs = {
                level: probs[0][i].item()
                for i, level in enumerate(self.LEVELS)
            }
        
        return {
            'level': predicted_level,
            'confidence': confidence_score,
            'probabilities': all_probs
        }
    
    def _predict_rule_based(self, features: ExperienceFeatures) -> Dict[str, Any]:
        """Rule-based prediction (fallback)"""
        years = features.years
        
        # Check job titles for level indicators
        title_level = None
        max_score = 0
        
        all_titles = " ".join([features.latest_title] + features.job_titles).lower()
        
        for level, keywords in self.LEVEL_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in all_titles)
            if score > max_score:
                max_score = score
                title_level = level
        
        # Years-based classification
        if years < 2:
            years_level = 'entry'
        elif years < 5:
            years_level = 'mid'
        elif years < 8:
            years_level = 'senior'
        else:
            years_level = 'expert'
        
        # Combine signals
        if title_level:
            # Trust title indicators more for higher levels
            if title_level in ['senior', 'expert'] and max_score >= 2:
                final_level = title_level
                confidence = 0.75
            else:
                # Average years and title
                levels_order = ['entry', 'mid', 'senior', 'expert']
                title_idx = levels_order.index(title_level)
                years_idx = levels_order.index(years_level)
                avg_idx = round((title_idx + years_idx) / 2)
                final_level = levels_order[avg_idx]
                confidence = 0.65
        else:
            final_level = years_level
            confidence = 0.60
        
        return {
            'level': final_level,
            'confidence': confidence,
            'years_based': years_level,
            'title_based': title_level
        }
    
    def _extract_features(self, resume_data: Dict[str, Any]) -> ExperienceFeatures:
        """Extract features from resume data"""
        
        # Calculate total years
        experience_entries = resume_data.get('experience', [])
        total_months = sum(entry.get('duration_months', 0) for entry in experience_entries)
        years = total_months / 12.0
        
        # Extract job titles
        job_titles = [
            entry.get('title', '') 
            for entry in experience_entries 
            if entry.get('title')
        ]
        
        # Get latest title
        latest_title = job_titles[0] if job_titles else ''
        
        # Extract responsibilities and achievements
        responsibilities = []
        achievements = []
        
        for entry in experience_entries:
            resp = entry.get('responsibilities', [])
            if isinstance(resp, list):
                responsibilities.extend(resp[:2])  # Top 2 per job
            
            ach = entry.get('achievements', [])
            if isinstance(ach, list):
                achievements.extend(ach[:1])  # Top 1 per job
        
        # Skills count
        skills = resume_data.get('skills', [])
        if isinstance(skills, dict):
            skills_count = len(skills.get('technical', [])) + len(skills.get('soft', []))
        else:
            skills_count = len(skills) if isinstance(skills, list) else 0
        
        # Education level
        education = resume_data.get('education', [])
        education_level = ''
        if education:
            highest = education[0]
            education_level = highest.get('degree', '')
        
        return ExperienceFeatures(
            years=years,
            job_titles=job_titles,
            responsibilities=responsibilities,
            achievements=achievements,
            latest_title=latest_title,
            skills_count=skills_count,
            education_level=education_level
        )
    
    def _generate_reasoning(self, features: ExperienceFeatures, level: str) -> str:
        """Generate human-readable reasoning"""
        reasons = []
        
        # Years
        years = features.years
        reasons.append(f"{years:.1f} years of experience")
        
        # Title analysis
        if features.latest_title:
            title = features.latest_title.lower()
            if any(kw in title for kw in self.LEVEL_KEYWORDS[level]):
                reasons.append(f"Current title '{features.latest_title}' indicates {level} level")
        
        # Skills
        if features.skills_count > 20:
            reasons.append(f"Extensive skill set ({features.skills_count} skills)")
        elif features.skills_count > 10:
            reasons.append(f"Solid skill set ({features.skills_count} skills)")
        
        # Experience breadth
        if len(features.job_titles) >= 4:
            reasons.append(f"Diverse experience ({len(features.job_titles)} positions)")
        
        return "; ".join(reasons)
    
    def train(self,
             train_data: List[Tuple[Dict[str, Any], str]],
             val_data: List[Tuple[Dict[str, Any], str]],
             epochs: int = 3,
             batch_size: int = 16,
             learning_rate: float = 2e-5) -> Dict[str, List[float]]:
        """
        Train the classifier
        
        Args:
            train_data: List of (resume_data, level_label) tuples
            val_data: Validation data
            epochs: Number of training epochs
            batch_size: Batch size
            learning_rate: Learning rate
            
        Returns:
            Training history
        """
        print(f"🎓 Training Experience Classifier...")
        print(f"   Train samples: {len(train_data)}")
        print(f"   Val samples: {len(val_data)}")
        print(f"   Epochs: {epochs}")
        print(f"   Batch size: {batch_size}")
        print(f"   Learning rate: {learning_rate}")
        
        # Prepare datasets
        train_features = [self._extract_features(data) for data, _ in train_data]
        train_labels = [self.LEVELS.index(label) for _, label in train_data]
        
        val_features = [self._extract_features(data) for data, _ in val_data]
        val_labels = [self.LEVELS.index(label) for _, label in val_data]
        
        # Optimizer and scheduler
        optimizer = AdamW(self.model.parameters(), lr=learning_rate)
        total_steps = len(train_data) * epochs // batch_size
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=0,
            num_training_steps=total_steps
        )
        
        # Loss function
        criterion = nn.CrossEntropyLoss()
        
        # Training loop
        for epoch in range(epochs):
            print(f"\n📈 Epoch {epoch + 1}/{epochs}")
            
            # Train
            self.model.train()
            train_loss = 0
            
            for i in range(0, len(train_data), batch_size):
                batch_features = train_features[i:i + batch_size]
                batch_labels = train_labels[i:i + batch_size]
                
                # Prepare batch
                texts = [self._prepare_text(f) for f in batch_features]
                
                # Tokenize
                batch_inputs = self.tokenizer.batch_encode_plus(
                    texts,
                    add_special_tokens=True,
                    max_length=256,
                    padding='max_length',
                    truncation=True,
                    return_attention_mask=True,
                    return_tensors='pt'
                )
                
                input_ids = batch_inputs['input_ids'].to(self.device)
                attention_mask = batch_inputs['attention_mask'].to(self.device)
                labels = torch.tensor(batch_labels).to(self.device)
                
                # Forward pass
                optimizer.zero_grad()
                logits = self.model(input_ids, attention_mask)
                loss = criterion(logits, labels)
                
                # Backward pass
                loss.backward()
                optimizer.step()
                scheduler.step()
                
                train_loss += loss.item()
            
            avg_train_loss = train_loss / (len(train_data) // batch_size)
            self.training_history['train_loss'].append(avg_train_loss)
            
            # Validation
            val_loss, val_acc = self._validate(val_features, val_labels, criterion, batch_size)
            self.training_history['val_loss'].append(val_loss)
            self.training_history['val_accuracy'].append(val_acc)
            
            print(f"   Train Loss: {avg_train_loss:.4f}")
            print(f"   Val Loss: {val_loss:.4f}")
            print(f"   Val Accuracy: {val_acc:.2%}")
        
        print("\n✅ Training complete!")
        return self.training_history
    
    def _validate(self,
                 features: List[ExperienceFeatures],
                 labels: List[int],
                 criterion: nn.Module,
                 batch_size: int) -> Tuple[float, float]:
        """Validate the model"""
        self.model.eval()
        total_loss = 0
        correct = 0
        
        with torch.no_grad():
            for i in range(0, len(features), batch_size):
                batch_features = features[i:i + batch_size]
                batch_labels = labels[i:i + batch_size]
                
                texts = [self._prepare_text(f) for f in batch_features]
                
                batch_inputs = self.tokenizer.batch_encode_plus(
                    texts,
                    add_special_tokens=True,
                    max_length=256,
                    padding='max_length',
                    truncation=True,
                    return_attention_mask=True,
                    return_tensors='pt'
                )
                
                input_ids = batch_inputs['input_ids'].to(self.device)
                attention_mask = batch_inputs['attention_mask'].to(self.device)
                labels_tensor = torch.tensor(batch_labels).to(self.device)
                
                logits = self.model(input_ids, attention_mask)
                loss = criterion(logits, labels_tensor)
                
                total_loss += loss.item()
                
                preds = torch.argmax(logits, dim=1)
                correct += (preds == labels_tensor).sum().item()
        
        avg_loss = total_loss / (len(features) // batch_size)
        accuracy = correct / len(features)
        
        return avg_loss, accuracy
    
    def save_model(self, path: str):
        """Save model weights"""
        path_obj = Path(path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'training_history': self.training_history,
            'model_name': self.model_name,
            'levels': self.LEVELS
        }, path)
        
        print(f"💾 Model saved to {path}")
    
    def load_model(self, path: str):
        """Load model weights"""
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.training_history = checkpoint.get('training_history', {})
        
        print(f"📂 Model loaded from {path}")


if __name__ == "__main__":
    print("=" * 70)
    print("🧪 Testing Experience Level Classifier")
    print("=" * 70)
    
    # Initialize classifier (without training for quick test)
    classifier = ExperienceLevelClassifier(
        model_name='bert-base-uncased',
        use_pretrained=False
    )
    
    # Test cases
    test_cases = [
        {
            'name': 'Entry Level - Recent Graduate',
            'resume': {
                'experience': [
                    {
                        'title': 'Software Engineering Intern',
                        'duration_months': 6,
                        'responsibilities': ['Wrote unit tests', 'Fixed bugs'],
                        'achievements': ['Deployed first feature']
                    }
                ],
                'skills': ['Python', 'Git', 'React'],
                'education': [
                    {'degree': 'Bachelor of Science in Computer Science'}
                ]
            },
            'expected': 'entry'
        },
        {
            'name': 'Mid Level - 3 Years',
            'resume': {
                'experience': [
                    {
                        'title': 'Software Engineer',
                        'duration_months': 36,
                        'responsibilities': ['Built microservices', 'Designed APIs'],
                        'achievements': ['Improved performance by 40%']
                    }
                ],
                'skills': ['Python', 'Django', 'AWS', 'Docker', 'PostgreSQL'],
                'education': [
                    {'degree': 'Bachelor of Science'}
                ]
            },
            'expected': 'mid'
        },
        {
            'name': 'Senior Level - 6 Years',
            'resume': {
                'experience': [
                    {
                        'title': 'Senior Software Engineer',
                        'duration_months': 36,
                        'responsibilities': ['Led team of 4', 'Architected systems'],
                        'achievements': ['Reduced costs by $200K']
                    },
                    {
                        'title': 'Software Engineer',
                        'duration_months': 36
                    }
                ],
                'skills': ['Python', 'Java', 'AWS', 'Kubernetes', 'Terraform', 
                          'React', 'Node.js', 'PostgreSQL', 'Redis'],
                'education': [
                    {'degree': 'Master of Science'}
                ]
            },
            'expected': 'senior'
        },
        {
            'name': 'Expert Level - 10 Years',
            'resume': {
                'experience': [
                    {
                        'title': 'Principal Engineer',
                        'duration_months': 48,
                        'responsibilities': ['Set technical strategy', 'Mentored 20+ engineers'],
                        'achievements': ['Led company-wide migration to cloud']
                    },
                    {
                        'title': 'Senior Software Engineer',
                        'duration_months': 36
                    },
                    {
                        'title': 'Software Engineer',
                        'duration_months': 36
                    }
                ],
                'skills': [f'Skill_{i}' for i in range(25)],  # 25 skills
                'education': [
                    {'degree': 'Master of Science'}
                ]
            },
            'expected': 'expert'
        }
    ]
    
    print("\n📝 Running test cases (rule-based mode)...\n")
    
    correct = 0
    for i, test in enumerate(test_cases, 1):
        print(f"{i}. {test['name']}")
        
        result = classifier.classify(
            test['resume'],
            use_hybrid=True,
            confidence_threshold=0.9  # Force rule-based for testing
        )
        
        level = result['level']
        confidence = result['confidence']
        method = result['method']
        reasoning = result['reasoning']
        
        is_correct = level == test['expected']
        correct += is_correct
        
        status = "✅" if is_correct else "❌"
        print(f"   {status} Predicted: {level} (expected: {test['expected']})")
        print(f"   Confidence: {confidence:.2%}")
        print(f"   Method: {method}")
        print(f"   Reasoning: {reasoning}")
        print()
    
    accuracy = correct / len(test_cases) * 100
    print("=" * 70)
    print(f"📊 Accuracy: {accuracy:.1f}% ({correct}/{len(test_cases)} correct)")
    print("=" * 70)
    
    print("\n💡 Note: This is using rule-based classification.")
    print("   For ML-based classification, train the model with labeled data.")
    print("   See the training example in the train() method docstring.")
