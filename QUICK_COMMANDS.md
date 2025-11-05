# 🚀 Quick Reference Commands

## Most Used Commands

### Start Backend
```bash
.\.venv\Scripts\activate
python src/api/main.py
```
*Backend runs on http://localhost:8000*

### Start Frontend
```bash
cd frontend
npm run dev
```
*Frontend runs on http://localhost:5173*

### API Documentation
```
http://localhost:8000/docs
```

---

## Installation Commands

### First Time Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_md

# Install frontend dependencies
cd frontend
npm install
cd ..
```

---

## Testing Commands

### Test Backend API
```python
# In Python console
import httpx
httpx.get("http://localhost:8000/health").json()
```

### Run Tests
```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_complete_pipeline.py -v

# Phase 1B tests
pytest tests/test_phase1_complete.py -v
```

---

## Common Tasks

### Upload Resume
```python
import httpx

with open("path/to/resume.pdf", "rb") as f:
    files = {"file": ("resume.pdf", f, "application/pdf")}
    response = httpx.post(
        "http://localhost:8000/api/v1/resumes/upload",
        files=files
    )
    print(response.json())
```

### Create Job
```python
import httpx

job_data = {
    "title": "Senior Python Developer",
    "description": "Looking for experienced Python developer...",
    "required_skills": ["Python", "FastAPI", "PostgreSQL"],
    "experience_required": "5+ years"
}

response = httpx.post(
    "http://localhost:8000/api/v1/jobs/",
    json=job_data
)
print(response.json())
```

### Find Matches
```python
import httpx

response = httpx.post(
    "http://localhost:8000/api/v1/matches/find",
    json={"job_id": 1, "top_k": 10}
)
print(response.json())
```

---

## Troubleshooting

### Kill Process on Port
```powershell
# Find process
netstat -ano | findstr :8000

# Kill process
taskkill /PID <PID> /F
```

### Reset Database
```bash
# Delete database
rm data/intellimatch.db

# Reinitialize
python -c "from src.core.db import init_db; init_db()"
```

### Clear Cache
```bash
# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +

# Clear pip cache
pip cache purge
```

---

## Git Commands

### Commit Changes
```bash
git add .
git commit -m "Your message"
git push origin main
```

### Check Status
```bash
git status
git log --oneline -10
```

---

*For full details, see: PHASE1C_1D_INTEGRATION_GUIDE.md*
