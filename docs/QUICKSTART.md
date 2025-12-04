# 🚀 IntelliMatch AI - Quick Start Guide

Get up and running with IntelliMatch AI in under 10 minutes!

---

## 📋 Prerequisites

- **Python 3.10+** installed
- **Windows PowerShell** (or Linux/Mac terminal)
- **8GB RAM minimum** (16GB recommended)
- **Internet connection** (for initial setup)

---

## ⚡ 5-Minute Setup

### 1. Clone & Navigate

```bash
cd d:\CKXJ\ML\TD1
```

### 2. Create Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

This installs:
- FastAPI + Uvicorn (API server)
- PyTorch + Transformers (ML)
- sentence-transformers (embeddings)
- FAISS-cpu (vector search)
- spaCy + langdetect (NLP)
- And 20+ other packages

**⏱️ Takes ~5 minutes**

### 4. Download Language Models

```powershell
python -m spacy download en_core_web_sm
python -m spacy download es_core_news_sm  # Spanish
python -m spacy download fr_core_news_sm  # French
```

---

## 🧪 Test the System

### Test 1: Quick Health Check

```powershell
python check_health.py
```

**Expected Output:**
```
✅ Phase 1 Pipeline: All modules loaded
✅ Skills Extractor: Ready
✅ Quality Scorer: Ready
✅ Experience Classifier: Ready
... (8 more checks)
```

### Test 2: Analyze a Resume

```powershell
python test_my_resume.py
```

**What it does:**
- Parses resume text
- Extracts skills with context
- Scores quality (1-10)
- Analyzes experience timeline
- Generates interview questions
- Detects bias flags

### Test 3: Full Integration Test

```powershell
python tests/test_phase1_pipeline_integration.py
```

**Expected Result:**
```json
{
  "language": "en",
  "quality": {
    "score": 7.5,
    "feedback": ["Add more metrics", "Quantify achievements"]
  },
  "skills": {
    "contextualized_skills": [
      {"skill": "Python", "context": "primary", "confidence": 0.95},
      {"skill": "Django", "context": "framework", "confidence": 0.90}
    ]
  },
  "timeline": {
    "total_years": 8.5,
    "gaps": [],
    "job_hopping_score": 0.2
  },
  "interview_questions": {
    "behavioral": [...],
    "technical": [...]
  }
}
```

---

## 🎯 Run Your First Analysis

### Analyze Your Own Resume

1. **Create a test file:**

```python
# test_my_resume_custom.py
from src.api.phase1_pipeline import analyze_resume

resume = {
    "text": """
    John Doe
    Senior Software Engineer
    
    Skills: Python, Django, AWS, Docker, PostgreSQL
    
    Experience:
    - Senior Engineer at TechCorp (2020-Present)
      Built microservices handling 10M+ requests/day
    
    - Software Engineer at StartupXYZ (2017-2020)
      Developed REST APIs with Django
    """,
    "skills": {"all_skills": ["Python", "Django", "AWS", "Docker", "PostgreSQL"]},
    "experience": [
        {
            "title": "Senior Engineer",
            "company": "TechCorp",
            "start_date": "2020-01",
            "end_date": "Present"
        }
    ]
}

result = analyze_resume(resume)
print(result)
```

2. **Run it:**

```powershell
python test_my_resume_custom.py
```

---

## 🌐 Start the API Server

### Option 1: Quick Start Script

```powershell
.\start.ps1
```

This starts both backend and frontend (if available).

### Option 2: Backend Only

```powershell
python src/api/main.py
```

Or:

```powershell
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 3: Production Mode

```powershell
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 📊 Access the System

Once the server is running:

- **API Docs (Swagger):** http://localhost:8000/docs
- **Alternative Docs (ReDoc):** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health
- **API Stats:** http://localhost:8000/api/v1/stats

---

## 🔑 Key API Endpoints

### 1. Analyze Resume

**POST** `/api/v1/analyze`

```json
{
  "text": "John Doe\nSenior Engineer...",
  "skills": {"all_skills": ["Python", "Django"]},
  "experience": [...]
}
```

**Returns:** Full analysis (quality, skills, timeline, questions, bias)

### 2. Match Resume to Job

**POST** `/api/v1/match`

```json
{
  "resume": {
    "text": "...",
    "skills": {...}
  },
  "job_description": {
    "text": "Looking for Senior Python Engineer...",
    "title": "Senior Backend Engineer"
  }
}
```

**Returns:** Match score + customized interview questions

### 3. Generate Interview Questions

**POST** `/api/v1/questions`

```json
{
  "resume": {...},
  "job_description": {...}
}
```

**Returns:** Behavioral + technical questions

---

## 📦 Working with Data

### Use Existing Training Data

We have **2,484 parsed resumes** ready to use:

```python
import json

# Load all resumes
with open('data/training/parsed_resumes_all.json', 'r') as f:
    resumes = json.load(f)

print(f"Loaded {len(resumes)} resumes")

# Analyze first resume
from src.api.phase1_pipeline import analyze_resume
result = analyze_resume(resumes[0])
```

### Access ESCO Skills Taxonomy

**851 validated skills** available:

```python
import json

with open('data/skills/validated_skills.json', 'r') as f:
    skills = json.load(f)

print(f"Available skills: {len(skills)}")
print(f"Example: {skills[0]}")
```

---

## 🧠 Training ML Models

### Generate Embeddings & FAISS Index

```powershell
# Open the training notebook
code notebooks/IntelliMatch_GPU_Training.ipynb
```

**Run all cells** (Ctrl+Alt+Enter) to:
1. Load 2,484 resumes
2. Generate embeddings (5-10 min on CPU)
3. Build FAISS index
4. Train experience classifier (10-20 min)

**Outputs:**
- `models/embeddings/resume_embeddings.npy`
- `models/embeddings/resume_faiss_index.bin`
- `models/embeddings/experience_classifier/`

### Use Pre-trained Models

If models already exist, they're automatically loaded:

```python
from src.services.matching_engine import MatchingEngine

engine = MatchingEngine()
engine.load_state('production')  # Loads embeddings & models
```

---

## 🧪 Testing

### Run All Tests

```powershell
# Full test suite
pytest tests/

# Specific test
python tests/test_phase1_pipeline_integration.py

# Test with verbose output
pytest tests/ -v

# Test with coverage
pytest tests/ --cov=src
```

### Interactive Testing Tool

```powershell
python tests/interactive_testing_tool.py
```

Interactive menu to:
- Test individual components
- Batch analyze resumes
- Generate reports
- Validate outputs

---

## 📈 Monitor Performance

### Check System Stats

```powershell
curl http://localhost:8000/api/v1/stats
```

```json
{
  "total_resumes": 2484,
  "total_jobs": 0,
  "total_matches": 0,
  "last_updated": "2025-11-24T10:30:00"
}
```

### Health Monitoring

```powershell
curl http://localhost:8000/health
```

```json
{
  "status": "healthy",
  "services": {
    "matching_engine": "up",
    "resume_parser": "up",
    "database": "up"
  }
}
```

---

## 🐛 Troubleshooting

### Issue: Import Errors

**Error:** `ModuleNotFoundError: No module named 'src'`

**Fix:**
```powershell
# Ensure you're in the project root
cd d:\CKXJ\ML\TD1

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Reinstall if needed
pip install -r requirements.txt
```

### Issue: spaCy Model Missing

**Error:** `Can't find model 'en_core_web_sm'`

**Fix:**
```powershell
python -m spacy download en_core_web_sm
```

### Issue: FAISS Not Found

**Error:** `No module named 'faiss'`

**Fix:**
```powershell
pip install faiss-cpu
```

### Issue: Port Already in Use

**Error:** `Address already in use: 8000`

**Fix:**
```powershell
# Use different port
uvicorn src.api.main:app --port 8001

# Or kill existing process
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process
```

---

## 📚 Next Steps

### For Developers

1. **Read** `COMPREHENSIVE_TESTING_PLAN.md` - Testing strategies
2. **Review** `src/ml/` - 10+ ML components
3. **Check** `tests/` - 20+ test files for examples
4. **Study** `src/api/phase1_pipeline.py` - Orchestration layer

### For Users

1. **Test** with your own resumes
2. **Experiment** with different job descriptions
3. **Explore** API endpoints via `/docs`
4. **Review** match explanations and feedback

### For Contributors

1. **Fork** the repository
2. **Create** feature branch
3. **Add** tests for new features
4. **Submit** pull request

---

## 🎯 Common Workflows

### Workflow 1: Analyze Single Resume

```powershell
# 1. Activate environment
.\.venv\Scripts\Activate.ps1

# 2. Run analysis
python test_my_resume.py

# 3. Review output
cat test_results/my_resume_analysis.json
```

### Workflow 2: Batch Process Resumes

```python
# batch_process.py
import json
from src.api.phase1_pipeline import analyze_resume

# Load resumes
with open('data/training/parsed_resumes_all.json', 'r') as f:
    resumes = json.load(f)

# Process batch
results = []
for resume in resumes[:100]:  # First 100
    result = analyze_resume(resume)
    results.append(result)

# Save results
with open('batch_results.json', 'w') as f:
    json.dump(results, f, indent=2)
```

### Workflow 3: API Integration

```python
# client_example.py
import requests

# Start API server first: python src/api/main.py

resume_data = {
    "text": "Your resume text here...",
    "skills": {"all_skills": ["Python", "Django"]},
    "experience": [...]
}

response = requests.post(
    "http://localhost:8000/api/v1/analyze",
    json=resume_data
)

result = response.json()
print(result)
```

---

## 📖 Additional Resources

- **Full Documentation:** `README.md`
- **Phase Plans:** `PHASE2_DETAILED_PLAN.md`, `PHASE3_DETAILED_PLAN.md`, etc.
- **Technical Reference:** `ref.md`
- **Project Summary:** `PROJECT_SUMMARY.md`
- **Session Notes:** `SESSION_SUMMARY_*.md`

---

## ✅ Verification Checklist

Before considering setup complete:

- [ ] Virtual environment activated
- [ ] All dependencies installed (`pip list` shows 40+ packages)
- [ ] spaCy models downloaded (en, es, fr)
- [ ] Health check passes (`python check_health.py`)
- [ ] Integration test passes
- [ ] API server starts without errors
- [ ] Can access http://localhost:8000/docs
- [ ] Sample resume analysis works

---

## 🎓 Learning Path

### Beginner: Understand the System

1. Run health check
2. Test with sample resume
3. Review API documentation
4. Explore generated outputs

### Intermediate: Modify & Extend

1. Add custom skills to taxonomy
2. Tune quality scorer thresholds
3. Create custom interview questions
4. Build new API endpoints

### Advanced: ML & Production

1. Train models with custom data
2. Optimize embeddings generation
3. Deploy to cloud (AWS/GCP)
4. Add monitoring & logging

---

## 🚀 You're Ready!

The system is now set up and ready to use. Start with `python test_my_resume.py` and explore from there!

**Questions?** Check the documentation or review test files for examples.

**Need Help?** All code is documented with comments and docstrings.

---

**Happy Resume Screening! 🎯**
