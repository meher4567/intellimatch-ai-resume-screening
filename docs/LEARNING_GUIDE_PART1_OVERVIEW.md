# IntelliMatch AI - Learning Guide Part 1: Topics & Usage Overview

## 📚 What This Guide Covers

This is **Part 1** of the comprehensive learning guide for IntelliMatch AI - an intelligent resume screening and candidate-job matching platform built using cutting-edge NLP and Machine Learning.

**Part 1** (This Document): Quick overview of all topics, technologies, and how they're used  
**Part 2** (Separate Document): In-depth explanations, concepts, implementation details, and learning path

---

## 🎯 Project Overview

**IntelliMatch AI** is an AI-powered recruitment automation platform that:
- Parses PDF/DOCX resumes and extracts 15+ fields automatically
- Matches candidates to jobs using semantic similarity and ML scoring
- Ranks candidates with tier-based system (S/A/B/C/D/F)
- Provides explainable AI with natural language match explanations
- Validates skills against ESCO taxonomy (851 validated skills)
- Calculates multi-factor scores (Skills 40%, Experience 30%, Education 20%, Quality 10%)

**Current Status:** Phase 1 Complete (85%) - Core ML Engine built and tested with 2,484 real resumes

---

## 📋 Topics & Technologies Used

### 1. **Natural Language Processing (NLP)**

#### 1.1 SpaCy for Text Processing
- **What:** Industrial-strength NLP library for text analysis
- **Used For:**
  - Named Entity Recognition (NER) - extracting person names, organizations
  - Part-of-Speech (POS) tagging - identifying nouns, verbs, technical terms
  - Dependency parsing - understanding sentence structure
  - Tokenization and lemmatization
- **Where:** `src/ml/dynamic_skill_extractor.py`, `src/ml/ner_extractor.py`
- **Model:** `en_core_web_md` (medium English model, 50MB)

#### 1.2 Pattern Matching & Regex
- **What:** Regular expressions for structured data extraction
- **Used For:**
  - Email extraction: `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`
  - Phone numbers: `(\+\d{1,3})?\s?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}`
  - Dates and experience timelines: `(\d{4})\s*-\s*(\d{4}|present)`
  - Skills with proficiency: `expert\s+(?:in|with|at)`, `\d{4,}\+?\s+years?`
- **Where:** `src/services/contact_extractor.py`, `src/ml/dynamic_skill_extractor.py`

#### 1.3 Text Similarity & Matching
- **What:** String matching algorithms for fuzzy matching
- **Used For:**
  - Skill alias resolution (ml → machine learning, aws → amazon web services)
  - Duplicate detection
  - Skill variant matching
- **Algorithms:** SequenceMatcher (Gestalt pattern matching), Levenshtein distance
- **Where:** `src/ml/scorers/skill_matcher.py`, `src/ml/esco_skill_mapper.py`

---

### 2. **Deep Learning & Transformers**

#### 2.1 Sentence-Transformers (BERT-based)
- **What:** Pre-trained transformer models for semantic embeddings
- **Model:** `all-MiniLM-L6-v2` (384-dimensional embeddings)
- **Used For:**
  - Converting resumes and job descriptions into vector representations
  - Semantic similarity calculation (cosine similarity)
  - Skill semantic matching (e.g., "python programming" ≈ "python developer")
- **Where:** `src/ml/embedding_generator.py`, `src/ml/skill_embedder.py`
- **Key Concepts:**
  - Embeddings: Dense vector representations capturing semantic meaning
  - Cosine similarity: Measures angle between vectors (0 to 1)
  - Batch processing: Efficient GPU/CPU encoding

#### 2.2 Experience Classification (BERT Fine-tuning)
- **What:** Custom BERT classifier trained to predict experience level
- **Model:** Fine-tuned DistilBERT (66M parameters)
- **Classes:** Entry, Mid, Senior, Expert
- **Training:** 2,484 resumes with manual labels
- **Used For:**
  - Automatic experience level prediction from resume text
  - Seniority matching between candidates and job requirements
- **Where:** `src/ml/trained_experience_classifier.py`, `src/ml/experience_classifier.py`

#### 2.3 PyTorch for ML Operations
- **What:** Deep learning framework
- **Used For:**
  - Loading pre-trained models
  - GPU acceleration (CUDA support)
  - Model fine-tuning and training
- **Where:** Throughout ML modules, especially embedding generation

---

### 3. **Vector Databases & Similarity Search**

#### 3.1 FAISS (Facebook AI Similarity Search)
- **What:** High-performance vector similarity search library
- **Used For:**
  - Indexing resume embeddings for fast retrieval
  - k-NN search: Finding top K similar resumes for a job
  - Efficient cosine similarity calculation at scale
- **Index Types:**
  - `IndexFlatIP`: Exact inner product search (cosine similarity)
  - GPU support for massive datasets (>10K resumes)
- **Where:** `src/ml/vector_store.py`

#### 3.2 Vector Store Architecture
- **What:** Custom wrapper around FAISS with metadata management
- **Features:**
  - Resume ID to vector mapping
  - Metadata storage (name, skills, experience, education)
  - Batch indexing and search
  - Persistence (save/load indexes)
- **Operations:**
  - `add()`: Index single resume
  - `search()`: Find similar resumes
  - `filter_by_metadata()`: Skill-based filtering
- **Where:** `src/ml/vector_store.py`

---

### 4. **Semantic Search & Information Retrieval**

#### 4.1 Hybrid Search Strategy
- **What:** Combining multiple search methods
- **Approach:**
  1. **Semantic Search**: Vector similarity (FAISS + embeddings)
  2. **Keyword Filtering**: Exact skill matches
  3. **Metadata Filtering**: Experience level, education requirements
  4. **Re-ranking**: Multi-factor scoring
- **Where:** `src/ml/semantic_search.py`

#### 4.2 Query Processing
- **What:** Converting job descriptions into searchable queries
- **Steps:**
  1. Parse job description (extract skills, experience, education)
  2. Generate job embedding
  3. Extract required skills
  4. Build metadata filters
- **Where:** `src/services/job_description_parser.py`, `src/ml/semantic_search.py`

---

### 5. **Machine Learning Scoring & Ranking**

#### 5.1 Multi-Factor Match Scoring
- **What:** Weighted scoring system combining multiple factors
- **Formula:**
  ```
  Final Score = (Semantic × 30%) + (Skills × 40%) + (Experience × 20%) + (Education × 10%)
  ```
- **Components:**
  - **Semantic Score**: Cosine similarity between resume and job embeddings (0-100)
  - **Skills Score**: Percentage of required skills matched + bonus for additional relevant skills
  - **Experience Score**: Match between candidate and required experience level
  - **Education Score**: Degree level match (PhD > Master's > Bachelor's)
- **Where:** `src/ml/match_scorer.py`

#### 5.2 Skill Matching with Semantic Understanding
- **What:** Intelligent skill comparison beyond exact string matching
- **Methods:**
  - **Exact Match**: Direct string comparison
  - **Alias Resolution**: ml → machine learning, k8s → kubernetes
  - **Semantic Match**: Embedding similarity (threshold: 0.75)
    - "python programming" ≈ "python development" (similarity: 0.92)
    - "machine learning" ≈ "artificial intelligence" (similarity: 0.81)
- **Scoring:**
  - Required skills matched: 100% weight
  - Nice-to-have skills: 50% weight
  - Extra relevant skills: Bonus points
- **Where:** `src/ml/scorers/skill_matcher.py`

#### 5.3 Experience Matching
- **What:** Comparing candidate experience with job requirements
- **Factors:**
  - **Years**: Exact match, underqualified penalty, overqualified handling
  - **Level**: Entry/Mid/Senior/Expert classification match
  - **Relevance**: Industry-specific experience boost
- **Scoring Logic:**
  ```python
  if candidate_years >= required_years:
      base_score = 100
      if candidate_years > required_years * 1.5:
          base_score = 85  # Overqualified penalty
  else:
      ratio = candidate_years / required_years
      base_score = ratio * 70  # Underqualified
  ```
- **Where:** `src/ml/scorers/experience_matcher.py`

#### 5.4 Candidate Ranking & Tiering
- **What:** Organizing candidates by match quality
- **Tiers:**
  - **S-Tier (85-100)**: Exceptional match - Top priority
  - **A-Tier (75-84)**: Excellent match - Strong candidates
  - **B-Tier (65-74)**: Good match - Consider for interview
  - **C-Tier (50-64)**: Fair match - Backup options
  - **D-Tier (<50)**: Weak match - Not recommended
- **Additional Metrics:**
  - Percentile ranking
  - Tier distribution statistics
  - Mean/median scores
- **Where:** `src/ml/candidate_ranker.py`

---

### 6. **Skill Extraction & Validation**

#### 6.1 Dynamic Skill Extraction
- **What:** Multi-method skill extraction with confidence scoring
- **Methods:**
  1. **NER-based**: SpaCy entity recognition for technical terms
  2. **Pattern Matching**: Regex for skill-like phrases (`proficient in X`, `experience with Y`)
  3. **Section-based**: Direct extraction from "Skills" section
  4. **Context-aware**: Skills mentioned in experience descriptions
- **Confidence Scoring:**
  - Explicit section mention: 1.0
  - Multiple mentions: +0.2 per occurrence
  - Context with proficiency: +0.3
  - Validated against taxonomy: +0.4
- **Where:** `src/ml/dynamic_skill_extractor.py`

#### 6.2 ESCO Skills Taxonomy
- **What:** European Skills, Competences, Qualifications and Occupations framework
- **Dataset:** 851 validated skills across 18 categories
- **Categories:**
  - Programming, Databases, Cloud/DevOps, Data Science/ML
  - Microsoft Office, Design, Project Management, Soft Skills
  - Business/Finance, Security, Networking, Web Technologies
  - Testing/QA, Operating Systems, Version Control, Languages
  - Industry-Specific, Certifications
- **Usage:**
  - Skill validation (is "Reactjs" a real skill?)
  - Standardization (JavaScript vs Javascript vs JS)
  - Noise filtering (removed 98.6% of junk skills)
- **Where:** `data/skills/validated_skills.json`, `src/ml/esco_skill_mapper.py`

#### 6.3 Proficiency Level Detection
- **What:** Automatically determining skill expertise level
- **Levels:** Expert, Advanced, Intermediate, Beginner
- **Indicators:**
  - **Expert**: "expert in", "mastery of", "4+ years", "lead developer"
  - **Advanced**: "strong knowledge", "proficient with", "2-3 years", "senior"
  - **Intermediate**: "working knowledge", "familiar with", "1-2 years"
  - **Beginner**: "basic understanding", "coursework in", "less than 1 year"
- **Where:** `src/ml/dynamic_skill_extractor.py` (lines 45-80)

#### 6.4 Skill Co-occurrence & Recommendations
- **What:** Learning which skills frequently appear together
- **Example:**
  - Python → NumPy, Pandas, Scikit-learn (Data Science stack)
  - React → JavaScript, HTML, CSS, Redux (Frontend stack)
  - Kubernetes → Docker, AWS, DevOps (Cloud stack)
- **Used For:**
  - Skill gap analysis
  - Skill recommendations ("You know Python, consider learning TensorFlow")
  - Skill clustering
- **Where:** `src/ml/skill_recommendation_engine.py`

---

### 7. **Resume Parsing & Document Processing**

#### 7.1 PDF Extraction
- **What:** Extracting text and structure from PDF files
- **Libraries:**
  - **PyMuPDF (fitz)**: Fast, accurate text extraction with layout preservation
  - **pdfplumber**: Table extraction, column detection
- **Challenges:**
  - Multi-column layouts (2-column resumes)
  - Headers/footers removal
  - Image-based PDFs (OCR required)
- **Where:** `src/services/pdf_extractor.py`

#### 7.2 DOCX Extraction
- **What:** Parsing Microsoft Word documents
- **Library:** `python-docx`
- **Features:**
  - Paragraph extraction
  - Table parsing
  - Bold/italic formatting detection (for section headers)
- **Where:** `src/services/docx_extractor.py`

#### 7.3 Section Detection
- **What:** Identifying resume sections (Education, Experience, Skills, etc.)
- **Methods:**
  - **Header matching**: Pattern-based detection of section titles
    - `r'^\s*(EDUCATION|ACADEMIC|QUALIFICATION)', r'^\s*(EXPERIENCE|EMPLOYMENT|WORK\s+HISTORY)'`
  - **Keyword clustering**: Grouping related content
  - **Position heuristics**: Typical resume structure
- **Sections Detected:**
  - Personal Info, Summary, Experience, Education, Skills, Certifications, Projects, Languages
- **Where:** `src/services/section_detector.py`

#### 7.4 Contact Information Extraction
- **What:** Extracting email, phone, LinkedIn, GitHub
- **Methods:**
  - **Email**: `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`
  - **Phone**: `(\+\d{1,3})?\s?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}`
  - **LinkedIn**: `linkedin\.com/in/[\w-]+`
  - **GitHub**: `github\.com/[\w-]+`
- **Where:** `src/services/contact_extractor.py`

#### 7.5 Name Extraction (Hybrid Approach)
- **What:** Identifying candidate name from resume
- **Methods:**
  1. **SpaCy NER**: Detecting PERSON entities
  2. **Position heuristic**: First non-empty line
  3. **Pattern matching**: Capitalized words at document start
  4. **ML-based**: Trained classifier (if first two fail)
- **Confidence Scoring**: Combining multiple signals
- **Where:** `src/ml/hybrid_name_extractor.py`, `src/services/name_extractor.py`

---

### 8. **Quality Assessment & Scoring**

#### 8.1 Resume Quality Scoring
- **What:** Evaluating resume completeness and quality (1-10 scale)
- **Factors:**
  - **Completeness** (40%): All required sections present
  - **Length** (20%): 300-2000 words optimal
  - **Structure** (20%): Clear sections, proper formatting
  - **Contact Info** (10%): Email, phone present
  - **Keywords** (10%): Technical skills, action verbs
- **Scoring:**
  ```
  Quality = (Completeness × 0.4) + (Length × 0.2) + (Structure × 0.2) + 
            (Contact × 0.1) + (Keywords × 0.1)
  ```
- **Where:** `src/ml/resume_quality_scorer.py`, `src/services/quality_scorer.py`

---

### 9. **REST API & Backend Architecture**

#### 9.1 FastAPI Framework
- **What:** Modern, fast Python web framework
- **Features:**
  - Automatic OpenAPI/Swagger documentation
  - Type validation with Pydantic
  - Async support
  - Dependency injection
- **Endpoints (48 total):**
  - `/api/v1/resumes` - Resume upload & management
  - `/api/v1/jobs` - Job posting management
  - `/api/v1/matches` - Match generation & retrieval
  - `/api/v1/candidates` - Candidate profiles
  - `/api/v1/skills` - Skills management
  - `/api/v1/analytics` - Hiring analytics
  - `/api/v1/auth` - Authentication
- **Where:** `src/main.py`, `src/api/*.py`

#### 9.2 SQLAlchemy ORM
- **What:** Object-Relational Mapping for database operations
- **Models:**
  - `Resume`: Parsed resume data (JSON storage)
  - `Job`: Job postings with requirements
  - `Match`: Resume-job matches with scores
  - `Candidate`: Candidate profiles
  - `User`: Authentication
- **Features:**
  - Relationships (one-to-many, many-to-many)
  - Soft deletes (`deleted_at` column)
  - Automatic timestamps
- **Where:** `src/models/*.py`

#### 9.3 PostgreSQL Database
- **What:** Relational database for structured data
- **Schema:**
  ```sql
  resumes: id, file_path, parsed_data_json, status, upload_date
  jobs: id, title, description, requirements_json, company, location
  matches: id, resume_id, job_id, score, explanation_json
  candidates: id, name, email, skills_json, experience_years
  ```
- **Indexes:** On frequently queried fields (status, upload_date, score)
- **Migrations:** Alembic for schema versioning
- **Where:** Database layer, `alembic/` for migrations

#### 9.4 Middleware & Security
- **Features:**
  - **CORS**: Cross-origin resource sharing for frontend
  - **Rate Limiting**: Custom per-client rate limits
    - Auth endpoints: 5-10 requests/hour
    - Upload endpoints: 20 requests/hour
    - Search endpoints: 100 requests/minute
  - **Request Logging**: Unique request IDs, timing, error tracking
  - **JWT Authentication**: Token-based auth (HS256, 30-minute expiry)
  - **Input Validation**: Pydantic schemas, file size limits (10MB)
- **Where:** `src/main.py`, `src/core/rate_limits.py`, `src/core/auth.py`

---

### 10. **Data Pipeline & Training**

#### 10.1 Training Dataset
- **What:** Collection of real resumes for ML training
- **Stats:**
  - **2,484 resumes** successfully parsed (98.6% success rate)
  - **928 unique validated skills** extracted
  - **18,957 skill mentions** total
  - **47.96 MB** JSON storage (`data/training/parsed_resumes_all.json`)
- **Processing:**
  - Bulk parsing with `train_on_all_resumes.py`
  - Quality filtering (scores < 3.0 excluded)
  - Skill validation against ESCO taxonomy
- **Where:** `data/training/`, `train_on_all_resumes.py`

#### 10.2 Feature Engineering
- **What:** Creating ML-ready features from raw data
- **Features Generated:**
  - Resume embeddings (384-dim vectors)
  - Skill frequency vectors
  - Experience timelines
  - Education level encoding
  - Co-occurrence matrices
- **Storage:** `data/training/training_features.json` (1.72 MB)
- **Where:** `scripts/` directory

#### 10.3 Model Training
- **What:** Fine-tuning ML models on resume data
- **Models Trained:**
  1. **Experience Classifier**: BERT fine-tuning for Entry/Mid/Senior/Expert
     - Training: 2,484 labeled examples
     - Accuracy: ~85% on validation set
  2. **Skill Embeddings**: Pre-computed for 851 ESCO skills
  3. **Resume Embeddings**: Batch generation for semantic search
- **Where:** `notebooks/` for Colab training, `models/` for saved weights

---

### 11. **Explainable AI & Match Explanations**

#### 11.1 Natural Language Explanations
- **What:** Generating human-readable match explanations
- **Template-Based Generation:**
  ```
  "[Candidate] is a [Tier] match for [Job Title]:
  
  ✅ Strengths:
  - [X] out of [Y] required skills matched ([%])
  - [Experience level] matches [requirement]
  - [Education level] meets requirements
  
  ⚠️ Areas for Development:
  - Missing skills: [skill1], [skill2]
  - [gap description]
  
  💡 Recommendation: [action]"
  ```
- **Where:** `src/ml/match_explainer.py`, `src/ml/advanced_match_explainer.py`

#### 11.2 Score Breakdown
- **What:** Detailed breakdown of match score components
- **Output:**
  ```json
  {
    "final_score": 78.5,
    "tier": "A-Tier",
    "breakdown": {
      "semantic": {"score": 82, "weight": 0.3, "contribution": 24.6},
      "skills": {"score": 85, "weight": 0.4, "contribution": 34.0},
      "experience": {"score": 70, "weight": 0.2, "contribution": 14.0},
      "education": {"score": 60, "weight": 0.1, "contribution": 6.0}
    },
    "explanation": "..."
  }
  ```
- **Where:** `src/ml/match_scorer.py`

---

### 12. **Deployment & Production**

#### 12.1 Docker Containerization
- **What:** Packaging application for consistent deployment
- **Services:**
  - `api`: FastAPI application
  - `db`: PostgreSQL database
  - `redis`: Caching and rate limiting
  - `nginx`: Reverse proxy with SSL
- **Files:** `Dockerfile`, `docker-compose.prod.yml`, `nginx.conf`

#### 12.2 Production Features
- **Monitoring:**
  - Health check endpoint (`/health`) with DB connectivity test
  - Request logging with unique IDs
  - Error tracking and stack traces
- **Performance:**
  - Response compression
  - Connection pooling (PostgreSQL)
  - Model caching (embeddings loaded once)
- **Security:**
  - Rate limiting per client
  - Input validation and sanitization
  - JWT authentication
  - Security headers (X-Frame-Options, X-Content-Type-Options)

---

## 🔧 Key Technical Concepts

### Embeddings
Dense vector representations of text that capture semantic meaning. Similar concepts have similar vectors.

### Cosine Similarity
Measures angle between two vectors. Range: -1 (opposite) to 1 (identical). Used for: 0.7+ = similar.

### Transfer Learning
Using pre-trained models (BERT, Sentence-Transformers) and fine-tuning for specific tasks.

### Multi-Factor Scoring
Combining multiple independent scores with weights to produce final decision.

### Soft Deletion
Marking records as deleted (`deleted_at` timestamp) instead of removing from database. Allows recovery.

### Vector Index
Data structure (FAISS) for fast similarity search in high-dimensional space. O(log n) vs O(n).

---

## 📊 Data Flow Summary

```
Resume Upload
    ↓
PDF/DOCX Extraction (PyMuPDF, python-docx)
    ↓
Text Preprocessing (SpaCy tokenization)
    ↓
Section Detection (Regex patterns)
    ↓
Field Extraction (NER, Contact, Skills)
    ↓
Skill Validation (ESCO taxonomy)
    ↓
Quality Scoring (Completeness, Length, Structure)
    ↓
Embedding Generation (Sentence-Transformers)
    ↓
Vector Store Indexing (FAISS)
    ↓
Database Storage (PostgreSQL)

Job Posting
    ↓
Job Parsing (Requirements extraction)
    ↓
Job Embedding Generation
    ↓
Semantic Search (FAISS k-NN)
    ↓
Multi-Factor Scoring (Skills, Experience, Education)
    ↓
Candidate Ranking (Tier assignment)
    ↓
Match Explanation Generation
    ↓
Results to API
```

---

## 🎓 Skills Demonstrated

### Machine Learning & AI
✅ Transformer models (BERT, Sentence-Transformers)  
✅ Transfer learning and fine-tuning  
✅ Vector embeddings and similarity search  
✅ Classification (experience level prediction)  
✅ Feature engineering  
✅ Model evaluation and validation  

### Natural Language Processing
✅ Named Entity Recognition (NER)  
✅ Text classification  
✅ Information extraction  
✅ Semantic similarity  
✅ Text preprocessing and normalization  

### Software Engineering
✅ REST API development (FastAPI)  
✅ Database design (PostgreSQL, SQLAlchemy ORM)  
✅ Clean architecture (separation of concerns)  
✅ Testing (unit, integration, end-to-end)  
✅ Version control (Git)  
✅ Documentation (code, API, guides)  

### MLOps & Production
✅ Docker containerization  
✅ Model serving and inference  
✅ Performance optimization  
✅ Monitoring and logging  
✅ Error handling and recovery  
✅ Security best practices  

### Data Engineering
✅ ETL pipelines  
✅ Data validation and cleaning  
✅ Feature engineering  
✅ Batch processing  
✅ Data versioning  

---

## 🔍 Where Each Component Lives

| Component | File Path | Purpose |
|-----------|-----------|---------|
| **Resume Parser** | `src/services/resume_parser.py` | Main parsing orchestration |
| **Skill Extractor** | `src/ml/dynamic_skill_extractor.py` | Multi-method skill extraction |
| **Embedding Generator** | `src/ml/embedding_generator.py` | Sentence-Transformer wrapper |
| **Vector Store** | `src/ml/vector_store.py` | FAISS index management |
| **Semantic Search** | `src/ml/semantic_search.py` | Search orchestration |
| **Match Scorer** | `src/ml/match_scorer.py` | Multi-factor scoring |
| **Candidate Ranker** | `src/ml/candidate_ranker.py` | Tier assignment & ranking |
| **Match Explainer** | `src/ml/match_explainer.py` | Natural language explanations |
| **Matching Engine** | `src/services/matching_engine.py` | Complete pipeline integration |
| **API Endpoints** | `src/api/*.py` | REST API routes |
| **Database Models** | `src/models/*.py` | SQLAlchemy ORM models |
| **ESCO Taxonomy** | `data/skills/validated_skills.json` | 851 validated skills |
| **Training Data** | `data/training/parsed_resumes_all.json` | 2,484 parsed resumes (48 MB) |

---

## 📈 Project Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| **Resumes Processed** | 2,484 | 98.6% success rate |
| **Skills Extracted** | 928 unique | Validated against ESCO |
| **Skill Noise Reduction** | 98.6% | From 65,518 to 928 |
| **API Endpoints** | 48 | Fully documented with OpenAPI |
| **ML Components** | 25+ | Modular, reusable |
| **Code Lines** | ~3,500+ | Production-ready |
| **Test Files** | 20+ | Comprehensive coverage |
| **Database Tables** | 8 | Normalized schema |
| **Embedding Dimension** | 384 | MiniLM model |
| **Average Processing Time** | ~2-3 seconds | Per resume |

---

## 🚀 Usage Examples

### 1. Parse Resume
```python
from src.services.resume_parser import ResumeParser

parser = ResumeParser(use_ml=True)
result = parser.parse("resume.pdf")
print(f"Name: {result['name']}")
print(f"Skills: {result['skills']['all_skills']}")
print(f"Quality: {result['quality_score']}/10")
```

### 2. Match Resume to Job
```python
from src.services.matching_engine import MatchingEngine

engine = MatchingEngine()
engine.index_resume(resume_data)
matches = engine.find_matches(job_data, top_k=10)

for match in matches:
    print(f"{match['name']}: {match['match_score']:.1f}% ({match['tier']})")
    print(f"Explanation: {match['explanation']}")
```

### 3. Extract Skills
```python
from src.ml.dynamic_skill_extractor import DynamicSkillExtractor

extractor = DynamicSkillExtractor()
skills = extractor.extract_skills(resume_text)

for skill in skills['all_skills']:
    print(f"{skill['skill']}: {skill['proficiency_level']} ({skill['confidence']:.2f})")
```

### 4. API Usage
```bash
# Upload resume
curl -X POST "http://localhost:8000/api/v1/resumes/upload" \
  -F "file=@resume.pdf"

# Find matches for job
curl "http://localhost:8000/api/v1/matches/find?job_id=1&min_score=70&limit=20"

# Get match explanation
curl "http://localhost:8000/api/v1/matches/1"
```

---

## 📚 Next: Part 2 - In-Depth Learning Guide

Part 2 covers:
- **Conceptual Deep Dives**: How BERT works, what are embeddings, understanding transformers
- **Algorithm Explanations**: Step-by-step breakdown of each ML component
- **Implementation Details**: Code walkthroughs, design decisions, trade-offs
- **Learning Path**: Recommended order to study topics, resources, exercises
- **Problem-Solving**: How we arrived at solutions, iterations, challenges faced
- **Extension Ideas**: How to add new features, improve existing ones

---

**Last Updated:** November 29, 2025  
**Version:** 1.0  
**Status:** Complete - Ready for learning
