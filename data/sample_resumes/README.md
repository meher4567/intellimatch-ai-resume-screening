# Sample Resume Sources

This document lists free sources where you can download real-world resume samples for testing.

## Option 1: Free Resume Templates (Download Ready)

### 1. Overleaf Gallery (LaTeX Resumes)
- **URL:** https://www.overleaf.com/gallery/tagged/cv
- **Formats:** PDF (LaTeX-generated, high quality)
- **How to download:**
  1. Visit the link above
  2. Click on any resume template (e.g., "Software Engineer CV", "Data Scientist Resume")
  3. Click "Open as Template" 
  4. Click "Download PDF" (top right)
  5. Save to `data/sample_resumes/real_world/`

**Recommended templates:**
- Deedy Resume (Software Engineer)
- Academic CV
- Modern CV

### 2. Resume.io Examples
- **URL:** https://resume.io/resume-examples
- **Formats:** PDF (professional quality)
- **How to download:**
  1. Visit the link
  2. Browse by profession (Software Engineer, Data Scientist, Product Manager, etc.)
  3. Click on example resume
  4. Right-click and "Save as PDF"

**Recommended examples:**
- Software Engineer Resume
- Data Analyst Resume
- Product Manager Resume

### 3. Indeed Resume Samples
- **URL:** https://www.indeed.com/career-advice/resume-samples
- **Formats:** Various (copyable text, some PDFs)
- **How to download:**
  1. Visit the link
  2. Search for your target role
  3. Copy text or download PDF (if available)

### 4. Zety Resume Examples
- **URL:** https://zety.com/blog/resume-examples
- **Formats:** PDF, DOCX
- **Note:** May require signup for full download

### 5. GitHub Resume Collections
- **URL:** https://github.com/topics/resume-template
- **Formats:** LaTeX, Markdown, PDF
- **How to download:**
  1. Find a repository (e.g., "awesome-cv", "resume")
  2. Download compiled PDF or generate from LaTeX

## Option 2: Create Your Own Test Resumes
✓ **Already done!** We created 3 sample resumes:
- `john_doe_simple` (Software Engineer)
- `sarah_chen_data_scientist` (Data Scientist)
- `michael_rodriguez_pm` (Product Manager)

Each available in 3 formats: TXT, PDF, DOCX

## Option 3: Use Your Own Resume

If you want to use your own resume:
1. Copy your resume file to `data/sample_resumes/`
2. Supported formats: PDF, DOCX
3. (Optional) Anonymize sensitive information:
   - Replace real name with "Test User"
   - Replace email with "test@example.com"
   - Replace phone with "(555) 000-0000"

## Directory Structure

```
data/
├── sample_resumes/
│   ├── john_doe_simple.txt/pdf/docx
│   ├── sarah_chen_data_scientist.txt/pdf/docx
│   ├── michael_rodriguez_pm.txt/pdf/docx
│   ├── real_world/                    # Real-world samples
│   │   ├── alex_kumar_complex.pdf/txt
│   │   ├── github_awesome_cv.pdf
│   │   └── my_resume.pdf
│   └── overleaf_templates/            # ✅ 22 Overleaf LaTeX templates
│       ├── akhil-kollas-resume.pdf
│       ├── ali-ozens-resume.pdf
│       └── ... (20 more)
└── generate_sample_resumes.py

Additional datasets (outside data/ folder):
sample_resumes/
├── synthetic_dataset/        # 300 AI-generated resumes
└── github_dataset/           # 50+ GitHub LaTeX templates
    └── popular_templates/    # 6 most popular
```

**Total Test Dataset: 451 PDF Resumes** ✅

## Tips for Downloading

1. **Quality:** Look for resumes with clear structure (Education, Experience, Skills)
2. **Variety:** Download different formats (single-column, two-column, creative layouts)
3. **Complexity:** Mix simple and complex resumes to test parser robustness
4. **Realistic:** Real-world resumes often have inconsistencies - good for testing!

## Next Steps

After downloading additional resumes:
1. Place them in `data/sample_resumes/real_world/`
2. Run the resume parser on all samples
3. Compare parsing accuracy across different formats
4. Identify edge cases that need special handling
