# Test Suite Documentation

## 🧪 **NEW: Manual Testing on 100 Resumes** ⭐

Before proceeding to Phase 1C, we're conducting comprehensive manual testing:

### **Testing Tools:**
- 📁 **`organize_test_dataset.py`** - Organize resumes into batches
- 🧪 **`interactive_testing_tool.py`** - Test resumes one-by-one with guided verification
- 📊 **`analyze_test_results.py`** - Generate comprehensive reports

### **Quick Start:**
```bash
# 1. Setup test directories
python tests/organize_test_dataset.py

# 2. Download 100 diverse resumes (see TESTING_GUIDE.md)

# 3. Start interactive testing
python tests/interactive_testing_tool.py

# 4. Analyze results
python tests/analyze_test_results.py
```

📖 **See `TESTING_GUIDE.md` and `COMPREHENSIVE_TESTING_PLAN.md` for complete instructions**

---

## 📁 Test Organization

All test files are organized in the `tests/` directory with clear naming conventions.

## 🧪 Comprehensive Tests

### **test_comprehensive_all_resumes.py** ⭐ PRIMARY TEST
**Purpose**: Complete end-to-end test on 72 real resumes  
**Coverage**:
- 22 Overleaf templates
- 50 GitHub dataset resumes
- Name extraction (97.2% success)
- Skill extraction (100% success)
- Quality scoring (5.2/10 average)
- Semantic skill matching

**Run**: `python tests/test_comprehensive_all_resumes.py`

---

## 🎯 Component Tests

### ML Integration Tests

**test_ml_integration.py**
- Tests all 3 ML extractors together
- HybridNameExtractor + SkillEmbedder + OrganizationExtractor
- 100% name accuracy, semantic skill matching

**test_semantic_skill_matcher.py**
- Tests semantic vs exact matching
- Shows 700% improvement (10/100 → 80/100)
- Abbreviation handling (ML → Machine Learning)

**test_quality_scorer.py**
- Resume quality scoring (1-10 scale)
- 6 quality factors
- Letter grades (A+ to F)
- Recommendations

**test_experience_classifier.py** ✨
- Experience level classification (Entry/Mid/Senior/Expert)
- Heuristic-based approach (no ML dependencies)
- Analyzes years + job titles
- 60-90% confidence scores
- Integrated into matching engine

**test_match_explainability.py** ✨ NEW
- Enhanced match explanations with feature importance
- Natural language explanations of match scores
- Top contributing factors identification
- Key matches and gaps analysis
- Actionable recommendations
- Visual contribution breakdowns
- Tests 3 different matching scenarios

### Extraction Tests

**test_ner_extraction.py**
- Basic spaCy NER extraction
- Names, organizations, locations, dates

**test_hybrid_all_resumes.py**
- Hybrid name extraction on 32 Overleaf resumes
- 100% accuracy validation

**test_skill_extraction.py**
- Semantic skill extraction
- 200+ skill database
- 7 categories

**test_organization_extraction.py**
- Company and university extraction
- Context-aware validation
- 65% noise reduction

### Dataset-Specific Tests

**test_all_overleaf_resumes.py**
- 22 Overleaf LaTeX templates
- Various resume styles

**test_github_resumes.py**
- GitHub dataset resumes
- Diverse international formats

**test_problem_resumes.py**
- Edge cases and difficult formats
- Error handling validation

### Phase Completion Tests

**test_phase1_complete.py**
- Phase 1A + 1B validation
- All ML components working

**test_week1_comprehensive.py**
- Week 1 milestone test

**test_week2_complete.py**
- Week 2 milestone test

### Feature-Specific Tests

**test_enhanced_sections.py**
- Section extraction accuracy

**test_projects_extraction.py**
- Project/achievement extraction

**test_my_resume*.py**
- Personal resume testing
- Real-world validation

**test_complete_pipeline.py**
- Full matching pipeline
- Match + Quality scores

---

## 📊 Test Results Summary

### Latest Comprehensive Test (72 Resumes):
```
✅ Parsing: 98.6% success (71/72)
✅ Name Extraction: 97.2% (69/71)
✅ Skill Extraction: 87.3% (62/71)
✅ Experience Classification: 64.8% (46/71)
📊 Average Skills: 10.1 per resume (max: 39)
⭐ Quality: 5.2/10 average
   - B grade: 50.7%
   - C grade: 16.9%
   - F grade: 28.2%
   - D grade: 4.2%
👤 Experience Levels:
   - Entry: 67.4%
   - Senior: 19.6%
   - Expert: 13.0%
```

### Semantic Skill Matching:
```
BEFORE: 10/100 (exact match)
AFTER:  80/100 (semantic match)
IMPROVEMENT: 700%
```

---

## 🚀 Running Tests

### Run All Tests:
```bash
# Full comprehensive test (recommended)
python tests/test_comprehensive_all_resumes.py

# ML integration
python tests/test_ml_integration.py

# Semantic matching
python tests/test_semantic_skill_matcher.py
```

### Run Specific Tests:
```bash
# Name extraction
python tests/test_hybrid_all_resumes.py

# Skill extraction
python tests/test_skill_extraction.py

# Organization extraction
python tests/test_organization_extraction.py

# Quality scoring
python tests/test_quality_scorer.py
```

---

## 📝 Test Data Locations

### Resumes:
- `data/sample_resumes/overleaf_templates/` - 22 LaTeX resumes
- `data/sample_resumes/github_dataset/` - 50 GitHub resumes
- `data/sample_resumes/real_world/` - Personal test resumes

### Test Results:
- `test_results/` - JSON outputs from test runs
- Timestamped files for tracking

---

## ✅ Validation Checklist

Before deployment, run these tests:

1. ☑ **test_comprehensive_all_resumes.py** - Full system test
2. ☑ **test_ml_integration.py** - ML components working
3. ☑ **test_semantic_skill_matcher.py** - Semantic matching active
4. ☑ **test_quality_scorer.py** - Quality assessment working

---

## 🎯 Test Coverage

### Parsing:
- ✅ PDF extraction (PyMuPDF + pdfplumber)
- ✅ DOCX extraction
- ✅ Multi-format support
- ✅ Error handling

### ML Extraction:
- ✅ spaCy NER (en_core_web_md)
- ✅ Sentence embeddings (all-MiniLM-L6-v2)
- ✅ Hybrid name extraction (100% accuracy)
- ✅ Semantic skill matching (700% improvement)
- ✅ Organization extraction (65% noise reduction)
- ✅ Experience level classification (64.8% coverage)
- ✅ Feature importance analysis (explainable AI)

### Quality Assessment:
- ✅ 6-factor scoring
- ✅ Letter grades
- ✅ Recommendations
- ✅ Strengths/weaknesses identification

### Matching Engine:
- ✅ Vector search (FAISS)
- ✅ Multi-factor scoring
- ✅ Semantic skill matching
- ✅ Quality scoring
- ✅ Experience level classification
- ✅ Candidate ranking
- ✅ Match explanations
- ✅ Feature importance analysis (explainable AI)

---

## 📈 Performance Metrics

| Component | Metric | Target | Actual |
|-----------|--------|--------|--------|
| Parsing | Success Rate | 95% | 98.6% ✅ |
| Name Extraction | Accuracy | 95% | 97.2% ✅ |
| Skill Extraction | Coverage | 85% | 87.3% ✅ |
| Experience Classification | Coverage | 60% | 64.8% ✅ |
| Semantic Matching | Improvement | 2x | 7x ✅ |
| Quality Scoring | Differentiation | Yes | Yes ✅ |

---

---

## 🆕 Experience Level Classifier

### Overview
**File**: `src/ml/experience_classifier.py`  
**Test**: `tests/test_experience_classifier.py`

Classifies candidates into experience levels based on resume content:
- **Entry**: < 2 years experience
- **Mid**: 2-5 years experience
- **Senior**: 5-10 years experience
- **Expert**: 10+ years experience

### How It Works
1. **Text Analysis**: Extracts years from experience descriptions
   - "5 years", "36 months", "6+ years"
2. **Keyword Detection**: Identifies seniority indicators
   - Senior, Lead, Principal, Manager, Director, etc.
3. **Confidence Scoring**: Returns 60-90% confidence based on clarity

### Integration
Integrated into `MatchingEngine` - every candidate automatically gets:
- `experience_level`: Entry/Mid/Senior/Expert
- `experience_confidence`: 0.0-1.0

### Run Tests
```bash
# Unit tests (5 test cases)
python tests/test_experience_classifier.py

# Integrated test (72 resumes)
python tests/test_comprehensive_all_resumes.py
```

### Results (72 Resumes)
- ✅ 64.8% successfully classified (46/71)
- 67.4% Entry level
- 19.6% Senior level
- 13.0% Expert level
- Average confidence: 60-80%

### No ML Dependencies
Uses heuristic rules only - no heavy ML models required. Can be upgraded to ML-based classification later if needed.

---

## 🔍 Enhanced Match Explainability

### Overview
**Files**: 
- `src/ml/explainability/match_explainer.py`
- `src/ml/explainability/feature_importance.py`
**Test**: `tests/test_match_explainability.py`

Provides comprehensive explanations for match scores with feature importance analysis.

### Key Features
1. **Feature Contribution Analysis**: Shows which factors contribute most to final score
2. **Natural Language Explanations**: Human-readable explanations of match results
3. **Top Contributing Factors**: Ranked list of what matters most
4. **Key Matches & Gaps**: Highlights strengths and weaknesses
5. **Actionable Recommendations**: For both recruiters and candidates
6. **Visual Breakdowns**: Text-based charts showing score distribution

### Example Output
```
Match Score: 82.5/100

Top Contributing Factors:
1. Skills       -  35.2 points (43%)
2. Semantic     -  25.5 points (31%)
3. Experience   -  15.6 points (19%)

Explanation:
This is a **strong match** - the candidate meets most requirements.
Skills contributed 35.2 points (43% of total score). 
Key skills matched include: Python, Django, PostgreSQL.
```

### Run Tests
```bash
# Comprehensive explainability test
python tests/test_match_explainability.py
```

### Results
- ✅ Natural language explanations working
- ✅ Feature importance calculated correctly
- ✅ Top factors identified accurately
- ✅ Visual breakdowns generated
- ✅ Recommendations actionable and relevant

---

**Last Updated**: November 1, 2025  
**Test Suite Version**: Phase 1B Complete (100%)  
**Total Tests**: 21+  
**Status**: All critical tests passing ✅  
**New Features**: Experience Classification + Enhanced Explainability
