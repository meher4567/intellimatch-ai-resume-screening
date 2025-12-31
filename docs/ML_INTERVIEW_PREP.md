# 🎯 IntelliMatch ML - Interview Prep & Improvement Guide

This document covers potential interview questions about your ML project and actionable improvements to strengthen it.

---

## 📋 Table of Contents
1. [Likely Interview Questions](#likely-interview-questions)
2. [Current Gaps & How to Fix](#current-gaps--how-to-fix)
3. [Quick Wins (1-2 hours each)](#quick-wins-1-2-hours-each)
4. [Medium Efforts (1-2 days each)](#medium-efforts-1-2-days-each)
5. [Improvement Roadmap](#improvement-roadmap)
6. [Code Templates](#code-templates)

---

## 🎤 Likely Interview Questions

### **Model Performance Questions**

#### Q1: "What are your model's precision and recall scores?"
**Current State**: ❌ Not measured  
**What They Want to Hear**: 
- "For skill extraction, we achieve 0.85 precision and 0.78 recall"
- "For experience classification, our F1-score is 0.82 across 4 classes"

**Action**: Run evaluation scripts (templates below)

---

#### Q2: "How did you validate your model? Did you use cross-validation?"
**Current State**: ❌ No formal cross-validation  
**What They Want to Hear**:
- "We used 5-fold stratified cross-validation"
- "Training/validation/test split of 70/15/15"
- "We ensured no data leakage between splits"

**Action**: Add K-fold CV to training scripts

---

#### Q3: "How do you handle class imbalance in experience classification?"
**Current State**: ⚠️ Likely imbalanced (more Entry-level than Expert)  
**What They Want to Hear**:
- "We used SMOTE for oversampling minority classes"
- "Applied class weights inversely proportional to frequency"
- "Used stratified sampling to preserve class distribution"

**Action**: Check class distribution, apply class weights

---

#### Q4: "What's your baseline? How much does your model improve over simple approaches?"
**Current State**: ❌ No baseline comparison  
**What They Want to Hear**:
- "Keyword matching baseline achieved 0.45 F1, our semantic model achieves 0.78"
- "TF-IDF + cosine similarity gave 0.62, BERT embeddings give 0.81"

**Action**: Implement simple baselines and compare

---

### **Architecture Questions**

#### Q5: "Why did you choose sentence-transformers over fine-tuned BERT?"
**Good Answer**:
- "Sentence-transformers are optimized for semantic similarity out-of-box"
- "Training data was limited (2,484 resumes) - fine-tuning risks overfitting"
- "Pre-trained models capture general language understanding well"
- "Trade-off: domain-specific fine-tuning could improve by 5-10%"

---

#### Q6: "How does your skill extraction handle skills not in ESCO taxonomy?"
**Current State**: ⚠️ May miss new/emerging skills  
**What They Want to Hear**:
- "We use fuzzy matching with 85% threshold for partial matches"
- "Unknown skills are flagged for human review"
- "We have a feedback loop to add validated new skills"

---

#### Q7: "How do you handle multi-language resumes?"
**Current State**: ✅ You have `multi_language_support.py`  
**Know Your Answer**:
- What languages are supported?
- What model handles translation/detection?
- What's the accuracy drop for non-English?

---

### **Production & Scale Questions**

#### Q8: "How would you handle 100,000 resumes per day?"
**Good Answer**:
- "FAISS allows sub-millisecond similarity search on millions of vectors"
- "Batch processing with GPU acceleration (currently using Colab)"
- "Async processing with task queue (Celery/Redis)"
- "Horizontal scaling with multiple API instances"

---

#### Q9: "How do you detect when the model needs retraining?"
**Current State**: ❌ No drift detection  
**What They Want to Hear**:
- "Monitor prediction distribution shifts"
- "Track average confidence scores over time"
- "Set up alerts when skill vocabulary changes significantly"
- "Scheduled quarterly retraining on new data"

---

#### Q10: "How do you ensure fairness/avoid bias in candidate ranking?"
**Current State**: ✅ You have `bias_detector.py`  
**Know Your Answer**:
- What biases do you check for? (gender, age, ethnicity indicators)
- How do you mitigate them?
- What metrics measure fairness?

---

### **Deep Learning Specific**

#### Q11: "Did you try fine-tuning BERT on resume data?"
**Current State**: ❌ Using pre-trained only  
**Honest Answer**:
- "We chose not to due to limited labeled data"
- "Pre-trained sentence-transformers showed strong performance"
- "Future work: domain adaptation with resume corpus"

---

#### Q12: "What loss function do you use for the matching scorer?"
**Know Your Answer**:
- Cosine similarity for embeddings
- Cross-entropy for classification tasks
- Custom weighted loss for multi-factor scoring?

---

## 🔧 Current Gaps & How to Fix

### Gap 1: No Formal Evaluation Metrics

**Problem**: Can't answer "what's your F1 score?"

**Fix**: Create `evaluate_models.py`

```python
# Run this to generate metrics for all components
from sklearn.metrics import classification_report, confusion_matrix
import json

# Skill Extraction Evaluation
# Experience Classification Evaluation  
# Match Scoring Evaluation
```

---

### Gap 2: No Baseline Comparison

**Problem**: Can't prove your model is better than simpler approaches

**Fix**: Implement baselines

| Task | Baseline | Your Model |
|------|----------|------------|
| Skill Extraction | Keyword matching | BERT + ESCO |
| Experience Classification | Years-based rules | Trained classifier |
| Resume Matching | TF-IDF cosine | Semantic embeddings |

---

### Gap 3: No Cross-Validation

**Problem**: Results may not be robust

**Fix**: Add to training scripts

```python
from sklearn.model_selection import StratifiedKFold

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
for fold, (train_idx, val_idx) in enumerate(skf.split(X, y)):
    # Train and evaluate
```

---

### Gap 4: No Model Versioning

**Problem**: Can't track experiments or roll back

**Fix**: Add MLflow (lightweight)

```python
import mlflow

mlflow.set_experiment("intellimatch")
with mlflow.start_run():
    mlflow.log_param("model", "sentence-transformers")
    mlflow.log_metric("f1", 0.82)
    mlflow.sklearn.log_model(model, "model")
```

---

## ⚡ Quick Wins (1-2 hours each)

### 1. Generate Classification Report for Experience Classifier
```python
# scripts/evaluate_experience_classifier.py
from sklearn.metrics import classification_report
# Load test data, run predictions, print report
```

### 2. Add Confusion Matrix Visualization
```python
import seaborn as sns
from sklearn.metrics import confusion_matrix
# Generate and save confusion matrix heatmap
```

### 3. Calculate Class Distribution
```python
# Show imbalance in your data
from collections import Counter
print(Counter(experience_levels))
```

### 4. Implement Simple Keyword Baseline
```python
# Compare to prove your model is better
def keyword_skill_matcher(text, skill_list):
    return [s for s in skill_list if s.lower() in text.lower()]
```

### 5. Add Confidence Scores to Predictions
```python
# Already may exist - ensure it's exposed
prediction, confidence = model.predict_with_confidence(text)
```

---

## 🛠️ Medium Efforts (1-2 days each)

### 1. Full Evaluation Pipeline
Create `scripts/full_evaluation.py`:
- Load test set (hold out 15% of data)
- Run all models
- Generate metrics JSON
- Create visualizations
- Save to `evaluation_results/`

### 2. Ablation Study
Test what happens when you remove each component:
- Without ESCO validation → how much noise increases?
- Without section detection → how much accuracy drops?
- Without semantic matching → just keyword matching?

### 3. Error Analysis
- Find the 50 worst predictions
- Categorize failure modes
- Document edge cases

### 4. Add Simple Model Monitoring
```python
# Log predictions to analyze later
def log_prediction(input_text, prediction, confidence, timestamp):
    with open('prediction_log.jsonl', 'a') as f:
        f.write(json.dumps({...}) + '\n')
```

### 5. Cross-Validation for Experience Classifier
- 5-fold stratified CV
- Report mean ± std for all metrics

---

## 📈 Improvement Roadmap

### Phase 1: Evaluation (Do First - 1 day)
- [ ] Create held-out test set (15% of 2,484 = ~370 resumes)
- [ ] Evaluate skill extraction precision/recall
- [ ] Evaluate experience classifier with classification report
- [ ] Evaluate quality scorer correlation with human ratings
- [ ] Generate confusion matrices

### Phase 2: Baselines (2-3 hours)
- [ ] Implement keyword matching for skills
- [ ] Implement rules-based experience classification
- [ ] Implement TF-IDF for resume similarity
- [ ] Compare all baselines to your models

### Phase 3: Robustness (1 day)
- [ ] Add 5-fold cross-validation
- [ ] Check and handle class imbalance
- [ ] Calculate confidence intervals

### Phase 4: Documentation (2-3 hours)
- [ ] Document all metrics in README
- [ ] Add evaluation results to docs
- [ ] Create performance comparison table

### Phase 5: Real Data Testing (1 day)
- [ ] Get 20-50 new resumes (different sources)
- [ ] Run full pipeline
- [ ] Document failure cases
- [ ] Identify patterns in errors

---

## 💻 Code Templates

### Template 1: Full Evaluation Script

```python
"""
scripts/evaluate_all_models.py
Run complete evaluation of all ML components
"""

import json
import numpy as np
from sklearn.metrics import (
    classification_report, 
    confusion_matrix,
    precision_recall_fscore_support,
    accuracy_score
)
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Output directory
EVAL_DIR = Path("evaluation_results")
EVAL_DIR.mkdir(exist_ok=True)

def evaluate_experience_classifier(test_data, predictions, labels):
    """Evaluate experience level classification"""
    
    # Get predictions
    y_true = [d['experience_level'] for d in test_data]
    y_pred = predictions
    
    # Classification report
    report = classification_report(y_true, y_pred, output_dict=True)
    print("\n=== EXPERIENCE CLASSIFIER ===")
    print(classification_report(y_true, y_pred))
    
    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', xticklabels=labels, yticklabels=labels)
    plt.title('Experience Classifier - Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(EVAL_DIR / 'experience_confusion_matrix.png')
    plt.close()
    
    return report

def evaluate_skill_extraction(test_data, extracted_skills, ground_truth_skills):
    """Evaluate skill extraction precision/recall"""
    
    total_precision = []
    total_recall = []
    total_f1 = []
    
    for i, (extracted, truth) in enumerate(zip(extracted_skills, ground_truth_skills)):
        extracted_set = set(s.lower() for s in extracted)
        truth_set = set(s.lower() for s in truth)
        
        if len(extracted_set) == 0:
            precision = 0
        else:
            precision = len(extracted_set & truth_set) / len(extracted_set)
        
        if len(truth_set) == 0:
            recall = 0
        else:
            recall = len(extracted_set & truth_set) / len(truth_set)
        
        if precision + recall == 0:
            f1 = 0
        else:
            f1 = 2 * (precision * recall) / (precision + recall)
        
        total_precision.append(precision)
        total_recall.append(recall)
        total_f1.append(f1)
    
    results = {
        'precision': np.mean(total_precision),
        'recall': np.mean(total_recall),
        'f1': np.mean(total_f1),
        'precision_std': np.std(total_precision),
        'recall_std': np.std(total_recall),
        'f1_std': np.std(total_f1)
    }
    
    print("\n=== SKILL EXTRACTION ===")
    print(f"Precision: {results['precision']:.3f} ± {results['precision_std']:.3f}")
    print(f"Recall: {results['recall']:.3f} ± {results['recall_std']:.3f}")
    print(f"F1 Score: {results['f1']:.3f} ± {results['f1_std']:.3f}")
    
    return results

def evaluate_quality_scorer(test_data, predicted_scores, human_ratings):
    """Evaluate quality scorer correlation with human ratings"""
    from scipy.stats import pearsonr, spearmanr
    
    pearson_corr, pearson_p = pearsonr(predicted_scores, human_ratings)
    spearman_corr, spearman_p = spearmanr(predicted_scores, human_ratings)
    
    results = {
        'pearson_correlation': pearson_corr,
        'pearson_pvalue': pearson_p,
        'spearman_correlation': spearman_corr,
        'spearman_pvalue': spearman_p,
        'mae': np.mean(np.abs(np.array(predicted_scores) - np.array(human_ratings))),
        'mse': np.mean((np.array(predicted_scores) - np.array(human_ratings))**2)
    }
    
    print("\n=== QUALITY SCORER ===")
    print(f"Pearson Correlation: {results['pearson_correlation']:.3f}")
    print(f"Spearman Correlation: {results['spearman_correlation']:.3f}")
    print(f"MAE: {results['mae']:.3f}")
    
    return results

def run_baseline_comparison():
    """Compare your model against simple baselines"""
    
    print("\n=== BASELINE COMPARISON ===")
    
    results = {
        'skill_extraction': {
            'keyword_matching': {'f1': 0.0},  # Fill after running
            'your_model': {'f1': 0.0}
        },
        'experience_classification': {
            'rules_based': {'f1': 0.0},
            'your_model': {'f1': 0.0}
        },
        'resume_matching': {
            'tfidf_cosine': {'ndcg': 0.0},
            'your_model': {'ndcg': 0.0}
        }
    }
    
    return results

if __name__ == "__main__":
    print("="*50)
    print("IntelliMatch ML - Full Evaluation")
    print("="*50)
    
    # Load your test data here
    # test_data = load_test_data()
    
    # Run evaluations
    # experience_results = evaluate_experience_classifier(...)
    # skill_results = evaluate_skill_extraction(...)
    # quality_results = evaluate_quality_scorer(...)
    # baseline_results = run_baseline_comparison()
    
    # Save results
    # all_results = {...}
    # with open(EVAL_DIR / 'evaluation_results.json', 'w') as f:
    #     json.dump(all_results, f, indent=2)
    
    print("\n✅ Evaluation complete! Results saved to evaluation_results/")
```

---

### Template 2: Cross-Validation Training

```python
"""
scripts/train_with_cv.py
Train experience classifier with 5-fold cross-validation
"""

import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import f1_score, accuracy_score
import json

def train_with_cross_validation(X, y, model_class, n_splits=5):
    """
    Train with stratified k-fold cross-validation
    
    Returns:
        dict with mean and std of all metrics
    """
    
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    
    fold_results = {
        'accuracy': [],
        'f1_macro': [],
        'f1_weighted': []
    }
    
    for fold, (train_idx, val_idx) in enumerate(skf.split(X, y)):
        print(f"\n--- Fold {fold + 1}/{n_splits} ---")
        
        X_train, X_val = X[train_idx], X[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]
        
        # Train model
        model = model_class()
        model.fit(X_train, y_train)
        
        # Predict
        y_pred = model.predict(X_val)
        
        # Calculate metrics
        acc = accuracy_score(y_val, y_pred)
        f1_mac = f1_score(y_val, y_pred, average='macro')
        f1_wgt = f1_score(y_val, y_pred, average='weighted')
        
        fold_results['accuracy'].append(acc)
        fold_results['f1_macro'].append(f1_mac)
        fold_results['f1_weighted'].append(f1_wgt)
        
        print(f"Accuracy: {acc:.4f}")
        print(f"F1 (macro): {f1_mac:.4f}")
        print(f"F1 (weighted): {f1_wgt:.4f}")
    
    # Calculate summary statistics
    summary = {}
    for metric, values in fold_results.items():
        summary[metric] = {
            'mean': np.mean(values),
            'std': np.std(values),
            'min': np.min(values),
            'max': np.max(values)
        }
    
    print("\n=== CROSS-VALIDATION SUMMARY ===")
    for metric, stats in summary.items():
        print(f"{metric}: {stats['mean']:.4f} ± {stats['std']:.4f}")
    
    return summary

# Example usage:
# summary = train_with_cross_validation(X, y, YourModelClass)
```

---

### Template 3: Baseline Implementations

```python
"""
scripts/baselines.py
Simple baseline implementations for comparison
"""

import re
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ============ SKILL EXTRACTION BASELINE ============
def keyword_skill_extractor(text, skill_list):
    """
    Simple keyword matching baseline for skill extraction
    """
    text_lower = text.lower()
    found_skills = []
    
    for skill in skill_list:
        # Simple substring matching
        if skill.lower() in text_lower:
            found_skills.append(skill)
    
    return found_skills

# ============ EXPERIENCE CLASSIFICATION BASELINE ============
def rules_based_experience_classifier(years_of_experience):
    """
    Simple rules-based baseline for experience level
    """
    if years_of_experience is None:
        return "Unknown"
    elif years_of_experience < 2:
        return "Entry"
    elif years_of_experience < 5:
        return "Mid"
    elif years_of_experience < 10:
        return "Senior"
    else:
        return "Expert"

def extract_years_from_resume(text):
    """
    Extract years of experience from resume text
    """
    patterns = [
        r'(\d+)\+?\s*years?\s*(?:of)?\s*experience',
        r'experience[:\s]+(\d+)\+?\s*years?',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return int(match.group(1))
    
    return None

# ============ RESUME MATCHING BASELINE ============
class TfidfMatcher:
    """
    TF-IDF based resume-job matching baseline
    """
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.resume_vectors = None
        self.resumes = None
    
    def fit(self, resumes):
        """Fit on corpus of resumes"""
        self.resumes = resumes
        texts = [r.get('text', '') for r in resumes]
        self.resume_vectors = self.vectorizer.fit_transform(texts)
    
    def match(self, job_description, top_k=10):
        """Find top-k matching resumes for a job"""
        job_vector = self.vectorizer.transform([job_description])
        similarities = cosine_similarity(job_vector, self.resume_vectors)[0]
        
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            results.append({
                'resume': self.resumes[idx],
                'score': similarities[idx]
            })
        
        return results

# ============ COMPARISON RUNNER ============
def compare_all_baselines(test_data):
    """
    Run all baselines and your models, compare results
    """
    
    results = {
        'skill_extraction': {},
        'experience_classification': {},
        'resume_matching': {}
    }
    
    # Your model results (fill these in)
    results['skill_extraction']['your_model'] = {'f1': 0.82}  # TODO
    results['experience_classification']['your_model'] = {'f1': 0.78}  # TODO
    results['resume_matching']['your_model'] = {'ndcg@10': 0.75}  # TODO
    
    # Baseline results (run baselines and fill)
    results['skill_extraction']['keyword'] = {'f1': 0.0}  # TODO
    results['experience_classification']['rules'] = {'f1': 0.0}  # TODO
    results['resume_matching']['tfidf'] = {'ndcg@10': 0.0}  # TODO
    
    # Calculate improvement
    for task in results:
        baseline_score = list(results[task].values())[1]['f1'] if 'f1' in list(results[task].values())[1] else list(results[task].values())[1].get('ndcg@10', 0)
        your_score = list(results[task].values())[0]['f1'] if 'f1' in list(results[task].values())[0] else list(results[task].values())[0].get('ndcg@10', 0)
        improvement = ((your_score - baseline_score) / baseline_score * 100) if baseline_score > 0 else 0
        print(f"{task}: +{improvement:.1f}% improvement over baseline")
    
    return results
```

---

### Template 4: Class Imbalance Check

```python
"""
scripts/check_class_imbalance.py
Analyze class distribution and handle imbalance
"""

import json
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np

def analyze_class_distribution(labels, class_name="Experience Level"):
    """
    Analyze and visualize class distribution
    """
    counts = Counter(labels)
    total = len(labels)
    
    print(f"\n=== {class_name} Distribution ===")
    print(f"Total samples: {total}")
    print("-" * 40)
    
    for label, count in counts.most_common():
        percentage = count / total * 100
        bar = "█" * int(percentage / 2)
        print(f"{label:15} {count:5} ({percentage:5.1f}%) {bar}")
    
    # Calculate imbalance ratio
    max_count = max(counts.values())
    min_count = min(counts.values())
    imbalance_ratio = max_count / min_count
    
    print("-" * 40)
    print(f"Imbalance ratio: {imbalance_ratio:.2f}x")
    
    if imbalance_ratio > 3:
        print("⚠️  HIGH IMBALANCE - Consider resampling or class weights")
    elif imbalance_ratio > 1.5:
        print("⚠️  MODERATE IMBALANCE - Consider class weights")
    else:
        print("✅ BALANCED - No action needed")
    
    # Visualize
    plt.figure(figsize=(10, 5))
    labels_sorted = [x[0] for x in counts.most_common()]
    values_sorted = [x[1] for x in counts.most_common()]
    
    plt.bar(labels_sorted, values_sorted, color='steelblue')
    plt.title(f'{class_name} Distribution')
    plt.xlabel('Class')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    
    for i, (label, value) in enumerate(zip(labels_sorted, values_sorted)):
        plt.text(i, value + 5, str(value), ha='center')
    
    plt.tight_layout()
    plt.savefig(f'class_distribution_{class_name.lower().replace(" ", "_")}.png')
    plt.close()
    
    return {
        'counts': dict(counts),
        'imbalance_ratio': imbalance_ratio,
        'recommendation': 'class_weights' if imbalance_ratio > 1.5 else 'none'
    }

def calculate_class_weights(labels):
    """
    Calculate class weights inversely proportional to frequency
    """
    counts = Counter(labels)
    total = len(labels)
    n_classes = len(counts)
    
    weights = {}
    for label, count in counts.items():
        weights[label] = total / (n_classes * count)
    
    print("\n=== Calculated Class Weights ===")
    for label, weight in sorted(weights.items(), key=lambda x: x[1], reverse=True):
        print(f"{label:15} weight: {weight:.3f}")
    
    return weights

# Example usage:
# with open('data/training/parsed_resumes_all.json') as f:
#     data = json.load(f)
# labels = [r.get('experience_level', 'Unknown') for r in data]
# analyze_class_distribution(labels)
# weights = calculate_class_weights(labels)
```

---

## 📊 Metrics You Should Know

After running evaluations, update these:

### Current Model Performance (TODO: Fill after evaluation)

| Component | Metric | Score | Baseline | Improvement |
|-----------|--------|-------|----------|-------------|
| Skill Extraction | F1 | ? | ? | +?% |
| Experience Classification | F1 (macro) | ? | ? | +?% |
| Experience Classification | Accuracy | ? | ? | +?% |
| Quality Scorer | Pearson r | ? | N/A | N/A |
| Resume Matching | NDCG@10 | ? | ? | +?% |

### Class Distribution (TODO: Fill after checking)

| Experience Level | Count | Percentage |
|------------------|-------|------------|
| Entry | ? | ?% |
| Mid | ? | ?% |
| Senior | ? | ?% |
| Expert | ? | ?% |

---

## 🎯 Interview Answer Cheat Sheet

### When Asked About Metrics:
> "Our skill extraction achieves [X] F1-score, compared to [Y] for simple keyword matching - a [Z]% improvement. For experience classification, we use stratified 5-fold CV and achieve [A] ± [B] F1-score."

### When Asked About Model Selection:
> "We chose sentence-transformers because they're optimized for semantic similarity tasks. Given our dataset size of 2,484 resumes, fine-tuning a full BERT model risked overfitting. The pre-trained embeddings capture general language understanding, and our ESCO taxonomy validation handles domain-specific skill matching."

### When Asked About Handling Edge Cases:
> "We've done error analysis on [X] failure cases. The main failure modes are: [1] skills mentioned in non-standard ways, [2] ambiguous experience descriptions, [3] non-English content. We handle these with fuzzy matching, context-aware extraction, and language detection."

### When Asked About Production:
> "For production scale, we use FAISS for sub-millisecond vector search. Embeddings are pre-computed and cached. We can handle [X] requests/second on current infrastructure. For monitoring, we log prediction confidence and flag low-confidence cases for review."

---

## ✅ Checklist Before Interview

- [ ] Run full evaluation script
- [ ] Know your F1/precision/recall numbers
- [ ] Know your baseline comparison numbers  
- [ ] Reviewed confusion matrix - can explain errors
- [ ] Checked class distribution
- [ ] Tested on 20+ new resumes, documented failures
- [ ] Can explain why you chose each model
- [ ] Can explain trade-offs you made
- [ ] Can discuss what you'd do with more time/data

---

## 🚀 Next Steps

1. **Today**: Run class distribution check
2. **Today**: Create test/train split (85/15)
3. **Tomorrow**: Run evaluation script, get real metrics
4. **Tomorrow**: Implement keyword baseline, compare
5. **Day 3**: Error analysis on worst predictions
6. **Day 4**: Test on new real resumes
7. **Day 5**: Update this doc with real numbers

---

*Last Updated: January 1, 2026*
