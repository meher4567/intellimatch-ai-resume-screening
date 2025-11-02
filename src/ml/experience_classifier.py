"""Experience Level Classifier

Lightweight classifier that uses sentence-transformers embeddings + a simple
sklearn classifier when available. Falls back to rule-based heuristics if
dependencies or a trained model aren't available.

Provides:
- ExperienceLevelClassifier.train(training_data)
- ExperienceLevelClassifier.predict(text_or_experience_list)
"""
from __future__ import annotations

import os
import re
import pickle
from typing import List, Tuple, Dict, Any

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None

try:
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import LabelEncoder
    import numpy as np
except Exception:
    LogisticRegression = None
    LabelEncoder = None
    np = None


class ExperienceLevelClassifier:
    """Predicts experience level: Entry / Mid / Senior / Expert

    The implementation will try to load a saved sklearn-based classifier
    (backed by sentence-transformers embeddings). If not available it will
    fall back to simple heuristics based on years and seniority keywords.
    """

    MODEL_PATH = os.path.join('models', 'experience_classifier.pkl')

    def __init__(self, embed_model: str = 'all-MiniLM-L6-v2'):
        self.embed_model_name = embed_model
        self.embedder = None
        self.clf = None
        self.le = None

        # Try to load embedder if available
        if SentenceTransformer is not None:
            try:
                self.embedder = SentenceTransformer(self.embed_model_name)
            except Exception:
                self.embedder = None

        # Try to load saved classifier
        if os.path.exists(self.MODEL_PATH):
            try:
                with open(self.MODEL_PATH, 'rb') as f:
                    data = pickle.load(f)
                    self.clf = data.get('clf')
                    self.le = data.get('le')
            except Exception:
                self.clf = None
                self.le = None

    # ------------------ Public API ------------------
    def train(self, training_data: List[Tuple[str, str]]) -> None:
        """Train a simple classifier.

        training_data: list of (text, label) where label in {Entry, Mid, Senior, Expert}
        """
        if LogisticRegression is None or SentenceTransformer is None:
            raise RuntimeError("Training requires scikit-learn and sentence-transformers")

        texts, labels = zip(*training_data)

        # Encode labels
        self.le = LabelEncoder()
        y = self.le.fit_transform(labels)

        # Compute embeddings
        X = self.embedder.encode(list(texts), show_progress_bar=False)

        # Train a small logistic regression
        self.clf = LogisticRegression(max_iter=1000)
        self.clf.fit(X, y)

        # Persist
        os.makedirs(os.path.dirname(self.MODEL_PATH), exist_ok=True)
        with open(self.MODEL_PATH, 'wb') as f:
            pickle.dump({'clf': self.clf, 'le': self.le}, f)

    def predict(self, experience: Any) -> Dict[str, Any]:
        """Predict experience level.

        Accepts either a textual summary or a list of experience entries (dicts).
        Returns: { 'level': str, 'confidence': float }
        """
        text = self._experience_to_text(experience)

        # If model available, use ML predictor
        if self.clf is not None and self.le is not None and self.embedder is not None:
            try:
                emb = self.embedder.encode([text], show_progress_bar=False)
                probs = self.clf.predict_proba(emb)[0]
                idx = int(probs.argmax())
                label = self.le.inverse_transform([idx])[0]
                confidence = float(probs[idx])
                return {'level': label, 'confidence': confidence}
            except Exception:
                pass

        # Fallback heuristic
        return self._heuristic_predict(text)

    # ------------------ Helpers ------------------
    def _experience_to_text(self, experience: Any) -> str:
        if isinstance(experience, str):
            return experience

        # If it's a list of dicts
        if isinstance(experience, list):
            parts = []
            for entry in experience:
                if isinstance(entry, dict):
                    parts.append(str(entry.get('title', '')))
                    parts.append(str(entry.get('company', '')))
                    parts.append(str(entry.get('achievements', '')))
                    parts.append(str(entry.get('duration_months', '')))
                else:
                    parts.append(str(entry))

            return ' '.join([p for p in parts if p])

        # Other types
        try:
            return str(experience)
        except Exception:
            return ""

    def _heuristic_predict(self, text: str) -> Dict[str, Any]:
        t = text.lower() if text else ''

        # Years-based heuristic
        years = self._extract_years(text)
        if years is not None:
            if years < 2:
                return {'level': 'Entry', 'confidence': 0.9}
            if 2 <= years < 5:
                return {'level': 'Mid', 'confidence': 0.85}
            if 5 <= years < 10:
                return {'level': 'Senior', 'confidence': 0.9}
            return {'level': 'Expert', 'confidence': 0.9}

        # Keyword-based fallback
        senior_keywords = ['senior', 'sr.', 'lead', 'principal', 'staff', 'head', 'director']
        expert_keywords = ['principal', 'distinguished', 'fellow']
        mid_keywords = ['mid', 'experienced', 'software engineer ii', 'software engineer iii']

        for kw in expert_keywords:
            if kw in t:
                return {'level': 'Expert', 'confidence': 0.8}

        for kw in senior_keywords:
            if kw in t:
                return {'level': 'Senior', 'confidence': 0.8}

        for kw in mid_keywords:
            if kw in t:
                return {'level': 'Mid', 'confidence': 0.75}

        # Default
        return {'level': 'Entry', 'confidence': 0.6}

    def _extract_years(self, text: str) -> int:
        if not text:
            return None

        # Look for patterns like '5 years', '6+ years', '3 yrs', '36 months'
        m = re.search(r"(\d{1,2})\+?\s*(years|yrs|year|months|month)", text.lower())
        if m:
            val = int(m.group(1))
            unit = m.group(2)
            if 'month' in unit:
                # Convert months to years (approx)
                years = val // 12
                return years
            return val

        # No years explicitly found
        return None


__all__ = ["ExperienceLevelClassifier"]
