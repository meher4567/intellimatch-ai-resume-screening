# 📝 Changelog

All notable changes to IntelliMatch are documented in this file.

---

## [2026-01-01] - Major Bug Fixes & System Validation

### 🐛 Bug Fixes

#### Experience Classifier Crashes
- **Fixed**: `slice(None, 20, None)` error in `TrainedExperienceClassifier`
  - **Cause**: Skills passed as dict `{'all_skills': [...]}` but code expected list
  - **Fix**: Added dict format detection in [trained_experience_classifier.py](../src/ml/trained_experience_classifier.py)
  ```python
  # Before
  skills = candidate_data.get('skills', [])
  text_parts.append(f"Skills: {', '.join(skills[:20])}")
  
  # After  
  skills_raw = candidate_data.get('skills', [])
  if isinstance(skills_raw, dict):
      skills = skills_raw.get('all_skills', [])
  elif isinstance(skills_raw, list):
      skills = skills_raw
  ```

#### Experience Duration Calculation Crashes
- **Fixed**: `unsupported operand type(s) for +: 'int' and 'NoneType'`
  - **Cause**: `duration_months` field was `None` for some experience entries
  - **Location 1**: [match_scorer.py](../src/ml/match_scorer.py) line 291-297
  - **Location 2**: [match_scorer.py](../src/ml/match_scorer.py) line 365-370 (fallback)
  - **Location 3**: [experience_matcher.py](../src/ml/scorers/experience_matcher.py) line 40
  ```python
  # Before
  total_months = sum(entry.get('duration_months', 0) for entry in experience_entries)
  
  # After
  total_months = 0
  for entry in experience_entries:
      months = entry.get('duration_months')
      if months is not None and isinstance(months, (int, float)):
          total_months += months
  ```

#### Experience Entry Title Crashes
- **Fixed**: AttributeError when `title` field is `None`
  - **Fix**: Added null check before calling `.lower()`
  ```python
  title = entry.get('title', '').lower() if entry.get('title') else ''
  ```

---

### ✨ New Features

#### Expanded Skill Alias System
Added 18 new skill aliases for better matching:

| Alias | Normalized To |
|-------|---------------|
| `node js`, `nodejs`, `node` | `node.js` |
| `react js`, `react.js` | `reactjs` |
| `vue js`, `vue.js` | `vuejs` |
| `python3`, `python 3`, `python 3.x` | `python` |
| `restful api`, `rest apis` | `restful api` |
| `mssql`, `ms sql` | `sql server` |

**Location**: [enhanced_skill_matcher.py](../src/ml/enhanced_skill_matcher.py) line 97-140

---

### 🧪 Testing Improvements

#### Created Comprehensive Evaluation Script
- **File**: [evaluate_matching_system.py](../scripts/evaluate_matching_system.py)
- Tests skill matching, multi-factor scoring, ranking, filtering
- Uses real data from 2,484 parsed resumes
- Fixed incorrect method/key names:
  - `match_skills` → `calculate_match_score`
  - `matched_required` → `required_matches`
  - `match_score` → `final_score`

#### Created Rigorous Test Suite
- **File**: [rigorous_system_test.py](../scripts/rigorous_system_test.py)
- **89 tests** across 9 test suites:
  1. Skill Matcher Edge Cases (15 tests)
  2. Fuzzy Matching Validation (22 tests)
  3. Semantic Matching Validation (8 tests)
  4. Scoring Consistency (4 tests)
  5. Match Scorer Multi-Factor (7 tests)
  6. Candidate Ranker Validation (12 tests)
  7. Real Data Stress Test (5 tests)
  8. Edge Case Bombing/Chaos (11 tests)
  9. Ranking Correctness (5 tests)

**Result**: 100% pass rate (89/89)

---

### 📊 Validation Results

#### Fuzzy Matching Confirmed Working
```
✅ Postgres → PostgreSQL (via alias)
✅ JS → JavaScript (via alias)
✅ Pythoon → Python (fuzzy 92%)
✅ Javascrpt → JavaScript (fuzzy 89%)
✅ Node JS → Node.js (via alias)
✅ Python3 → Python (via alias)
```

#### Semantic Matching Confirmed Working
```
✅ Web Development ↔ Frontend Development
✅ Backend Development ↔ Server-side Programming
✅ Data Analysis ↔ Data Analytics
❌ Python ↔ Cooking (correctly rejected)
❌ Machine Learning ↔ Gardening (correctly rejected)
```

#### Ranking Correctness Confirmed
```
#1 | 79.6 | Perfect Match - Senior
#2 | 75.2 | Good Match - Mid
#3 | 51.5 | Partial Match - Junior
#4 | 47.6 | Wrong Stack - Senior
#5 | 41.9 | Entry Level
```
✅ Perfect candidate ranks first
✅ Wrong stack candidate ranks lower despite more experience
✅ Entry level ranks last

---

### 📚 Documentation

#### Created Documentation
- [WHAT_MAKES_THIS_SPECIAL.md](WHAT_MAKES_THIS_SPECIAL.md) - Unique features explained
- [ML_INTERVIEW_PREP.md](ML_INTERVIEW_PREP.md) - Interview preparation guide
- This CHANGELOG.md

---

## [Previous] - Initial Development

### Core Components Built
- Resume parser with PDF/DOCX support
- ESCO skill taxonomy integration (851 skills)
- Enhanced skill matcher (Exact + Fuzzy + Semantic)
- Multi-factor match scorer
- Candidate ranker with tier system
- Experience classifier (BERT-based)
- FastAPI REST endpoints
- React frontend with dark theme

### Data Pipeline
- Processed 2,484 resumes
- Extracted 928 unique skills
- 18,957 skill mentions total
- 98.6% noise reduction

---

## Known Issues

### Low Priority
- Education data extraction is minimal (0% of resumes have education parsed)
- Experience classifier sometimes has low confidence (uses fallback)
- Performance: 500 candidates in ~5 min with full ML classification

### Workarounds in Place
- Fallback rule-based experience classification when BERT confidence < 70%
- None value handling throughout scoring pipeline
- Dict/list format detection for skill inputs

---

*This changelog follows [Keep a Changelog](https://keepachangelog.com/) format.*
