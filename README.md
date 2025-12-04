# 🎯 IntelliMatch AI - Intelligent Resume Screening Platform

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An AI-powered intelligent resume screening and candidate-job matching platform using state-of-the-art NLP and Deep Learning.

---

## 📢 Quick Start

**👉 [Read COMPLETE_GUIDE.md](COMPLETE_GUIDE.md) for everything you need to know!**

---

## 🎯 What is This?

**IntelliMatch AI** automates resume screening using:
- 🤖 Semantic matching with BERT/sentence-transformers
- 🎯 ESCO skill validation (851 validated skills)
- 📊 Multi-factor scoring (Skills 40%, Experience 30%, Education 20%, Quality 10%)
- 📈 Tier-based ranking (S/A/B/C/D/F)
- 💡 Explainable AI with natural language explanations

---

## 📊 Current Status

**Phase 1: Core ML Engine - 85% Complete** ✅

### ✅ What's Working
- 2,484 resumes processed (98.6% success)
- 928 unique validated skills (98.6% noise reduction!)
- 10+ ML/NLP components built
- Experience classification (Entry/Mid/Senior/Expert)
- Quality scoring (1-10 scale)
- Comprehensive test suite (20+ files)

### 🔄 In Progress
- GPU embedding generation (Google Colab - 95% done)

### ⏳ Next
- Phase 2: REST API Development (2-3 weeks)
- Phase 3: Frontend (6-8 weeks)
- Phase 4: Production Deployment (1-2 weeks)

---

## 🚀 Quick Commands

```bash
# Setup
.\.venv\Scripts\Activate.ps1              # Activate environment
pip install -r requirements.txt           # Install dependencies

# Test
python test_my_resume.py                  # Test your resume
python test_dynamic_skills.py             # Test skill extraction
python tests/test_comprehensive_all_resumes.py  # Full suite

# Train
python train_on_all_resumes.py            # Train on 2,484 resumes
python download_esco_skills.py            # Update skills taxonomy
```

---

## 🏗️ Architecture

```
Frontend (React) → REST API (FastAPI) → ML Engine (Phase 1 ✅)
                                        ├─ Resume Parser
                                        ├─ Skill Extractor (ESCO)
                                        ├─ Experience Classifier
                                        ├─ Quality Scorer
                                        ├─ Semantic Search (FAISS)
                                        ├─ Match Scorer
                                        ├─ Candidate Ranker
                                        └─ Match Explainer
```

---

## 💾 Key Data Assets

- **851 ESCO skills** in taxonomy (`data/skills/validated_skills.json`)
- **2,484 parsed resumes** (`data/training/parsed_resumes_all.json` - 52MB)
- **928 unique skills** extracted and validated
- **18,957 skill mentions** across dataset

---

## 📚 Documentation

- **[COMPLETE_GUIDE.md](COMPLETE_GUIDE.md)** - 📖 All-in-one comprehensive documentation
- **[ref.md](ref.md)** - 🔧 Technical reference implementations
- **[PHASE2_DETAILED_PLAN.md](PHASE2_DETAILED_PLAN.md)** - Phase 2 specs
- **[PHASE3_DETAILED_PLAN.md](PHASE3_DETAILED_PLAN.md)** - Phase 3 specs
- **[PHASE4_DETAILED_PLAN.md](PHASE4_DETAILED_PLAN.md)** - Phase 4 specs
- **[PHASE5_DETAILED_PLAN.md](PHASE5_DETAILED_PLAN.md)** - Phase 5 specs

---

## 🛠️ Tech Stack

**Backend:** FastAPI + Python 3.10+ + Uvicorn  
**ML/NLP:** PyTorch, Transformers, sentence-transformers, spaCy  
**Vector DB:** FAISS (GPU-optimized)  
**Database:** PostgreSQL + SQLAlchemy  
**Frontend:** React 18 + TypeScript + TailwindCSS (Phase 3)  
**Deployment:** Docker + AWS/GCP (Phase 4)

---

## 📁 Project Structure

```
TD1/
├── COMPLETE_GUIDE.md          ⭐ START HERE - Complete documentation
├── README.md                  📄 This file - Quick overview
├── ref.md                     🔧 Technical reference
├── src/
│   ├── ml/                    🧠 10+ ML/NLP components
│   ├── services/              ⚙️ Business logic (parser, matcher)
│   └── api/                   🌐 REST API endpoints (Phase 2)
├── data/
│   ├── skills/                📊 851 ESCO validated skills
│   └── training/              📦 2,484 parsed resumes (52MB)
├── tests/                     🧪 20+ test files
└── notebooks/                 📓 Google Colab training
```

---

## 🎯 Key Achievements

✅ **98.6% noise reduction** in skill extraction (65,518 → 928 skills)  
✅ **2,484 resumes** successfully parsed  
✅ **ESCO taxonomy integration** (851 validated skills)  
✅ **10+ ML components** built and tested  
✅ **Production-grade code** (~3,500+ lines)  
✅ **Comprehensive testing** (20+ test files)

---

## 🚀 Next Steps

1. Complete GPU embedding generation (15 min)
2. Integrate embeddings into matching (2-3 hours)
3. Start Phase 2 - REST API development (2-3 weeks)
4. Build frontend interface (6-8 weeks)
5. Deploy to production (1-2 weeks)

---

## 🎓 Learning Outcomes

This project demonstrates mastery of:
- ✅ Transformers & Deep Learning (BERT, sentence-transformers)
- ✅ NLP (NER, semantic similarity, information extraction)
- ✅ MLOps (GPU training, vector databases, FAISS)
- ✅ Software Engineering (clean architecture, testing, documentation)
- ✅ Production Systems (FastAPI, PostgreSQL, Docker)

---

## 📄 License

MIT License

---

## 👨‍💻 Author

**Portfolio Project** - Demonstrating ML/NLP engineering expertise

---

## 📞 Need Help?

1. **Read** [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md) - Has everything!
2. **Check** test files for examples
3. **Review** component source code in `src/ml/`

---

**⭐ For complete documentation, setup guides, testing instructions, and development workflow, see [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md)**