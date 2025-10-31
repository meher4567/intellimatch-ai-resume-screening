# IntelliMatch AI - Quick Start Guide

## Prerequisites

- Python 3.10 or higher
- PostgreSQL 15+ (optional for now, can develop without it)
- Git

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/meher4567/intellimatch-ai-resume-screening.git
cd intellimatch-ai-resume-screening
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
```

**Activate** (Windows PowerShell):
```powershell
.venv\Scripts\Activate.ps1
```

**Activate** (Windows CMD):
```cmd
.venv\Scripts\activate.bat
```

**Activate** (Linux/Mac):
```bash
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

**Note**: First installation may take 5-10 minutes (PyTorch, transformers are large).

### 4. Optional: Install spaCy Language Model
```bash
python -m spacy download en_core_web_sm
```

## Configuration

### Create `.env` File
```env
# Database (optional for testing services)
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/intellimatch

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-change-in-production

# Debug
DEBUG=True
```

## Testing Core Services (Without Database)

### Run Service Tests
```bash
python test_services.py
```

This will test:
- Resume parsing
- Skill extraction
- Semantic matching
- Knockout filtering

**Expected output**:
```
============================================================
IntelliMatch AI - Core Services Test Suite
============================================================

=== Testing Skill Extractor ===
Extracted 8 skills:
  - Python (Programming Language) - confidence: 0.9
  - React (Web Framework) - confidence: 0.9
  ...
✓ Skill extraction working!

=== Testing Resume Parser ===
Name: John Doe
Email: john.doe@email.com
...
✓ Resume parsing working!

=== Testing Matching Engine ===
Match Results:
  Overall Score: 78.5%
  ...
✓ Matching engine working!

✓ All tests passed!
```

## Running the API (Requires Database)

### 1. Set Up PostgreSQL

**Option A: Docker (Recommended)**
```bash
docker run -d \
  --name intellimatch-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=intellimatch \
  -p 5432:5432 \
  postgres:15
```

**Option B: Local Installation**
1. Install PostgreSQL from https://www.postgresql.org/download/
2. Create database:
```sql
CREATE DATABASE intellimatch;
```

### 2. Run Database Migrations
```bash
alembic upgrade head
```

This creates all tables (User, Resume, Job, Match, etc.)

### 3. Start the API Server
```bash
uvicorn src.main:app --reload
```

**Access**:
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Using the API

### 1. Upload a Resume

**Via Swagger UI**:
1. Go to http://localhost:8000/docs
2. Find `POST /api/v1/resumes/upload`
3. Click "Try it out"
4. Upload a PDF or DOCX file
5. Execute

**Via cURL**:
```bash
curl -X POST "http://localhost:8000/api/v1/resumes/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@resume.pdf"
```

**Response**:
```json
{
  "id": 1,
  "candidate_id": 1,
  "file_path": "data/raw/20231031_120000_resume.pdf",
  "file_type": "application/pdf",
  "source": "upload",
  "status": "parsed",
  "upload_date": "2023-10-31T12:00:00"
}
```

### 2. Create a Job Posting

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/jobs/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Python Developer",
    "description": "We are looking for an experienced Python developer with Django and AWS experience.",
    "requirements": "5+ years Python, Django, PostgreSQL, AWS, Docker",
    "location": "Remote",
    "employment_type": "full-time",
    "salary_range": "$120,000 - $150,000"
  }'
```

### 3. Create a Match (Auto-Scoring)

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/matches/" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_id": 1,
    "job_id": 1
  }'
```

**Response**:
```json
{
  "id": 1,
  "resume_id": 1,
  "job_id": 1,
  "score": 85.7,
  "status": "new",
  "created_at": "2023-10-31T12:05:00"
}
```

The matching engine automatically:
1. Extracts skills from resume and job
2. Computes semantic similarity
3. Calculates skill match score
4. Returns weighted overall score

### 4. List Top Matches for a Job

```bash
curl "http://localhost:8000/api/v1/matches/job/1?limit=10"
```

### 5. Schedule an Interview

```bash
curl -X POST "http://localhost:8000/api/v1/interviews/" \
  -H "Content-Type: application/json" \
  -d '{
    "match_id": 1,
    "scheduled_date": "2023-11-05T14:00:00",
    "meeting_link": "https://zoom.us/j/123456789"
  }'
```

## API Endpoints Overview

### Resumes
- `POST /api/v1/resumes/upload` - Upload and parse resume

### Jobs
- `POST /api/v1/jobs/` - Create job
- `GET /api/v1/jobs/` - List jobs (paginated)
- `GET /api/v1/jobs/{id}` - Get job details
- `PUT /api/v1/jobs/{id}` - Update job
- `DELETE /api/v1/jobs/{id}` - Delete job

### Matches
- `POST /api/v1/matches/` - Create match (with auto-scoring)
- `GET /api/v1/matches/` - List matches
- `GET /api/v1/matches/job/{id}` - Matches for job
- `GET /api/v1/matches/resume/{id}` - Matches for resume
- `PUT /api/v1/matches/{id}` - Update match
- `DELETE /api/v1/matches/{id}` - Delete match

### Interviews
- `POST /api/v1/interviews/` - Schedule interview
- `GET /api/v1/interviews/` - List interviews
- `PUT /api/v1/interviews/{id}` - Update interview

### Status & Notes
- `POST /api/v1/status-notes/status` - Update status
- `GET /api/v1/status-notes/status/{match_id}` - Get status history
- `POST /api/v1/status-notes/note` - Add note
- `GET /api/v1/status-notes/note/{type}/{id}` - Get notes

### Analytics
- `GET /api/v1/analytics/dashboard` - Dashboard metrics
- `GET /api/v1/analytics/skills` - Top skills
- `GET /api/v1/analytics/events` - Analytics events

## Development Workflow

### 1. Make Code Changes
Edit files in `src/` directory

### 2. Format Code
```bash
black src/
```

### 3. Lint Code
```bash
flake8 src/
```

### 4. Run Tests
```bash
pytest
```

### 5. Create Migration (if models changed)
```bash
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

## Project Structure

```
intellimatch-ai-resume-screening/
├── src/
│   ├── api/           # API endpoints
│   ├── core/          # Config, database, dependencies
│   ├── models/        # SQLAlchemy models
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Business logic
│   └── main.py        # FastAPI app
├── alembic/           # Database migrations
├── data/
│   └── raw/           # Uploaded resumes
├── tests/             # Unit tests
├── requirements.txt   # Dependencies
├── .env              # Environment variables
└── test_services.py  # Service test suite
```

## Troubleshooting

### Issue: "ModuleNotFoundError"
**Solution**: Ensure virtual environment is activated and dependencies installed:
```bash
pip install -r requirements.txt
```

### Issue: "Could not load model all-MiniLM-L6-v2"
**Solution**: First run downloads the model (~80MB). Wait for download to complete.

### Issue: "Connection refused" when starting API
**Solution**: Ensure PostgreSQL is running:
```bash
# Check if running (Windows)
Get-Service postgresql*

# Start service (Windows)
Start-Service postgresql-x64-15
```

### Issue: "Table doesn't exist"
**Solution**: Run migrations:
```bash
alembic upgrade head
```

### Issue: Resume parsing fails
**Solution**: 
- Ensure file is valid PDF or DOCX
- Check file size (must be < 10MB)
- Some PDFs are scanned images (OCR not yet implemented)

## Performance Tips

### Speed Up Matching
- First match takes ~5 seconds (model loading)
- Subsequent matches: ~200ms each
- Use batch processing for multiple resumes
- Consider caching embeddings in Redis

### GPU Acceleration
If you have NVIDIA GPU:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Production Deployment
- Use Gunicorn instead of Uvicorn
- Enable Redis caching
- Use CDN for file storage
- Set DEBUG=False
- Use environment secrets
- Enable HTTPS
- Set up monitoring (Sentry, DataDog, etc.)

## Next Steps

1. ✅ Test core services (no database needed)
2. ⏳ Set up PostgreSQL database
3. ⏳ Run Alembic migrations
4. ⏳ Start API and test endpoints
5. ⏳ Upload sample resumes
6. ⏳ Create jobs and test matching
7. ⏳ Build frontend dashboard

## Resources

- **API Documentation**: http://localhost:8000/docs (when running)
- **Project Plan**: `PROJECT_MASTER_PLAN.md`
- **Development Status**: `DEVELOPMENT_STATUS.md`
- **Services README**: `src/services/README.md`

## Support

For issues or questions:
- Check `DEVELOPMENT_STATUS.md` for current progress
- Review `src/services/README.md` for service documentation
- Test services with `python test_services.py`
- Check Swagger UI for API details

---

**Happy Coding! 🚀**
