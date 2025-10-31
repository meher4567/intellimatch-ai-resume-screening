# IntelliMatch AI - Core Services

This document describes the core business logic services implemented in the IntelliMatch AI system.

## Services Overview

### 1. Resume Parser (`resume_parser.py`)

**Purpose**: Extract text and structured data from resume files (PDF, DOCX).

**Key Features**:
- PDF text extraction using PyMuPDF
- DOCX text extraction using python-docx
- Email extraction (regex pattern matching)
- Phone number extraction
- Name extraction (heuristic-based)
- Basic skill extraction (keyword matching)
- Education degree detection
- Experience estimation

**Usage**:
```python
from src.services.resume_parser import ResumeParser

parser = ResumeParser()
result = parser.parse_file("path/to/resume.pdf")

# Result contains:
# - raw_text: Full extracted text
# - email: Extracted email address
# - phone: Phone number
# - name: Candidate name
# - skills: List of identified skills
# - education: Degrees found
# - experience_years: Estimated years of experience
```

**Supported Formats**: `.pdf`, `.docx`, `.doc`

---

### 2. Skill Extractor (`skill_extractor.py`)

**Purpose**: Identify and normalize skills from text using NLP and pattern matching.

**Key Features**:
- Comprehensive skill database (100+ skills)
- Keyword matching with word boundaries
- Skill normalization (e.g., "js" → "JavaScript")
- Skill categorization (Programming Language, Framework, Database, etc.)
- Pattern-based extraction for compound skills
- Optional spaCy NLP extraction
- Confidence scoring

**Usage**:
```python
from src.services.skill_extractor import SkillExtractor

extractor = SkillExtractor()
skills = extractor.extract_skills(resume_text)

# Each skill contains:
# - name: Canonical skill name
# - category: Skill category
# - confidence: Match confidence (0-1)
# - matched_text: Original text that matched

# Normalize a skill name
canonical = extractor.normalize_skill("nodejs")  # Returns "Node.js"

# Get skill category
category = extractor.categorize_skill("Python")  # Returns "Programming Language"
```

**Skill Categories**:
- Programming Language
- Web Framework
- Database
- Cloud
- DevOps
- AI/ML
- Data Science
- Methodology
- Soft Skill

---

### 3. Matching Engine (`matching_engine.py`)

**Purpose**: Compute semantic similarity and rank candidates against job descriptions.

**Key Features**:
- Sentence transformer embeddings (all-MiniLM-L6-v2)
- Cosine similarity computation
- Multi-factor scoring:
  - Semantic similarity (40% weight)
  - Skill matching (40% weight)
  - Keyword matching (20% weight)
- Candidate ranking
- Match explanation with matched/missing skills
- Knockout criteria filtering

**Usage**:
```python
from src.services.matching_engine import MatchingEngine

matcher = MatchingEngine()

# Compute similarity between resume and job
score = matcher.compute_similarity(resume_text, job_description)

# Comprehensive matching with breakdown
match_result = matcher.match_resume_to_job(
    resume_text=resume_text,
    job_description=job_description,
    resume_skills=["Python", "React", "AWS"],
    job_requirements=["Python", "Django", "Docker"]
)

# Result contains:
# - semantic_similarity: Embedding similarity score
# - skill_match: Skill overlap score
# - keyword_match: Keyword overlap score
# - overall_score: Weighted average (0-1)
# - percentage: Overall score as percentage

# Rank multiple candidates
ranked = matcher.rank_candidates(
    resumes=[
        {"text": resume1, "skills": skills1},
        {"text": resume2, "skills": skills2}
    ],
    job_description=job_desc,
    job_requirements=["Python", "AWS"],
    top_k=10
)

# Explain match with details
explanation = matcher.explain_match(
    resume_text, job_description,
    resume_skills, job_requirements
)
# Returns matched_skills, missing_skills, and score breakdown
```

**Knockout Filtering**:
```python
from src.services.matching_engine import KnockoutFilter

passes, reasons = KnockoutFilter.apply_filters(
    candidate_data={
        "experience_years": 3,
        "skills": ["Python", "React"],
        "education": "Bachelor of Science"
    },
    knockout_criteria=[
        {"type": "min_experience", "value": 2},
        {"type": "required_skill", "value": "Python"}
    ]
)
```

---

## Integration with API

### Resume Upload Flow

1. User uploads resume file via `/api/v1/resumes/upload`
2. File is validated (extension, size)
3. ResumeParser extracts text and metadata
4. SkillExtractor identifies skills
5. Candidate record is created/updated
6. Resume record is created with parsed data
7. Response includes parsed information

### Matching Flow

1. User creates match via `/api/v1/matches/`
2. MatchingEngine computes similarity score
3. SkillExtractor identifies skills from both resume and job
4. Multi-factor score is calculated
5. Match record is created with score
6. Response includes detailed match breakdown

---

## Configuration

### Environment Variables

None required for basic operation. Optional:

```env
# Use larger model for better quality (slower)
MATCHING_MODEL=all-mpnet-base-v2

# Enable spaCy NLP extraction (requires: python -m spacy download en_core_web_sm)
USE_NLP_EXTRACTION=true
```

---

## Dependencies

**Core**:
- `PyMuPDF` - PDF text extraction
- `python-docx` - DOCX text extraction
- `python-magic-bin` - File type detection

**ML/NLP**:
- `sentence-transformers` - Semantic embeddings
- `torch` - PyTorch backend
- `scikit-learn` - Similarity metrics
- `spacy` - NLP (optional)

**Install**:
```bash
pip install PyMuPDF python-docx python-magic-bin sentence-transformers torch scikit-learn

# Optional: spaCy with English model
pip install spacy
python -m spacy download en_core_web_sm
```

---

## Performance Notes

- **Resume parsing**: ~1-2 seconds per file
- **Skill extraction**: ~100ms per document
- **Semantic matching**: 
  - First call: ~5 seconds (model loading)
  - Subsequent calls: ~200ms per comparison
  - Batch processing: More efficient

**Optimization tips**:
- Cache sentence transformer model in memory
- Batch encode multiple texts together
- Use Redis to cache computed embeddings
- Consider using quantized models for faster inference

---

## Testing

Example test resume:
```python
from src.services.resume_parser import ResumeParser

parser = ResumeParser()
result = parser.parse_file("test_resume.pdf")

assert result['email'] is not None
assert len(result['skills']) > 0
assert result['name'] is not None
```

---

## Future Enhancements

1. **Resume Parser**:
   - OCR for scanned PDFs
   - Multi-language support
   - Section detection (Work Experience, Education, etc.)
   - Date parsing for employment history

2. **Skill Extractor**:
   - Machine learning-based skill extraction
   - Skill proficiency level detection
   - Technology stack inference
   - Domain expertise identification

3. **Matching Engine**:
   - Fine-tuned model for job matching
   - Contextual matching (industry-specific)
   - Diversity-aware ranking
   - Explainable AI for match decisions
   - Real-time matching with streaming data

---

## Troubleshooting

**Issue**: "Could not load model all-MiniLM-L6-v2"
**Solution**: First run downloads the model (~80MB). Ensure internet connection.

**Issue**: "Error parsing PDF"
**Solution**: Some PDFs are scanned images. Consider adding OCR (tesseract).

**Issue**: "spaCy model not found"
**Solution**: Run `python -m spacy download en_core_web_sm`

**Issue**: Slow matching performance
**Solution**: 
- Use GPU if available (PyTorch will detect automatically)
- Batch process multiple resumes
- Cache embeddings in Redis
- Use smaller model (all-MiniLM-L6-v2 instead of all-mpnet-base-v2)
