"""
Script to download sample resumes from public sources
This automates downloading real-world resume examples for testing
"""

import requests
import os
from pathlib import Path

# Directory setup
SCRIPT_DIR = Path(__file__).parent
SAMPLE_DIR = SCRIPT_DIR / 'sample_resumes' / 'real_world'
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

def download_file(url, filename):
    """Download a file from URL and save it"""
    try:
        print(f"Downloading: {filename}...")
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        filepath = SAMPLE_DIR / filename
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"✓ Downloaded: {filename} ({len(response.content)} bytes)")
        return True
    except Exception as e:
        print(f"✗ Failed to download {filename}: {str(e)}")
        return False

def download_github_resumes():
    """Download sample resumes from GitHub repositories"""
    print("\n=== Downloading from GitHub ===")
    
    # These are direct links to PDF resumes from public repositories
    github_resumes = [
        {
            'url': 'https://github.com/sb2nov/resume/raw/master/deedy_resume-openfont.pdf',
            'filename': 'github_deedy_cv.pdf',
            'description': 'Deedy Resume (Software Engineer)'
        },
        {
            'url': 'https://github.com/posquit0/Awesome-CV/raw/master/examples/resume.pdf',
            'filename': 'github_awesome_cv.pdf',
            'description': 'Awesome CV (Data Engineer)'
        },
    ]
    
    for resume in github_resumes:
        print(f"\n{resume['description']}")
        download_file(resume['url'], resume['filename'])

def download_overleaf_samples():
    """Download sample resumes from Overleaf (if direct links available)"""
    print("\n=== Overleaf Templates ===")
    print("Note: Overleaf resumes require manual download from:")
    print("https://www.overleaf.com/gallery/tagged/cv")
    print("\nRecommended templates to download manually:")
    print("1. 'Deedy Resume' - Modern single-column layout")
    print("2. 'Academic CV' - Traditional academic format")
    print("3. 'Software Engineer CV' - Tech-focused template")
    print("\nSteps:")
    print("1. Visit the URL above")
    print("2. Click on a template")
    print("3. Click 'Open as Template'")
    print("4. Click 'Download PDF' (top right)")
    print(f"5. Save to: {SAMPLE_DIR}")

def create_sample_complex_resume():
    """Create a more complex resume with special characters and formatting"""
    print("\n=== Creating Complex Test Resume ===")
    
    complex_content = """ALEX KUMAR
alex.kumar@email.com | +1-555-234-5678 | San José, CA
Portfolio: alexkumar.io | GitHub: @alexk | LinkedIn: /in/alex-kumar

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROFESSIONAL SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Full-stack developer with 7+ years building scalable web applications. Expert in JavaScript/TypeScript,
React, Node.js, and cloud architecture. Led teams of 5-10 engineers. Passionate about clean code & UX.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TECHNICAL EXPERTISE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Languages:      JavaScript, TypeScript, Python, Java, Go, SQL
Frontend:       React, Next.js, Vue.js, Angular, Redux, TailwindCSS, Material-UI
Backend:        Node.js, Express, NestJS, Django, FastAPI, Spring Boot
Databases:      PostgreSQL, MongoDB, Redis, MySQL, Elasticsearch, DynamoDB
Cloud/DevOps:   AWS (Lambda, ECS, S3, CloudFront), Docker, Kubernetes, Terraform, Jenkins
Tools:          Git, JIRA, Figma, Postman, GraphQL, REST APIs, WebSocket

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROFESSIONAL EXPERIENCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Lead Software Engineer | TechCorp Global Inc. | 2021 - Present
San Francisco, CA

► Led architecture redesign reducing API latency from 500ms → 80ms (84% improvement)
► Managed team of 8 engineers across 3 time zones (US, Europe, Asia)
► Implemented CI/CD pipeline increasing deployment frequency from weekly → daily
► Built microservices architecture handling 10M+ requests/day
► Tech: React, Node.js, PostgreSQL, Redis, AWS (ECS, Lambda, S3), Docker, Kubernetes

Key Achievement: Designed real-time collaboration feature (like Google Docs) used by 100K+ users

─────────────────────────────────────────────────────────────────────

Senior Full-Stack Developer | StartupXYZ (Acquired by BigTech) | 2018 - 2021
New York, NY

► Core team member (employee #5) that grew product from 0 → 500K users
► Built customer dashboard with 95% satisfaction score (measured via NPS)
► Integrated payment system (Stripe) processing $2M+ monthly transactions
► Optimized database queries reducing load time by 60%
► Tech: Next.js, TypeScript, GraphQL, MongoDB, AWS (S3, CloudFront, Lambda)

Key Achievement: Led development of MVP that secured $5M Series A funding

─────────────────────────────────────────────────────────────────────

Software Engineer | E-Commerce Giant | 2016 - 2018
Seattle, WA

► Developed product recommendation engine increasing conversion by 25%
► Built A/B testing framework used by 20+ teams across organization
► Mentored 3 junior engineers through code reviews & pair programming
► Tech: React, Redux, Node.js, Java, MySQL, Redis, Elasticsearch

─────────────────────────────────────────────────────────────────────

Junior Developer | Digital Agency | 2015 - 2016
Austin, TX

► Developed responsive websites for 15+ clients (retail, healthcare, finance)
► Collaborated with designers using Figma/Sketch for pixel-perfect implementation
► Tech: HTML, CSS, JavaScript, jQuery, WordPress, PHP

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EDUCATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Master of Science in Computer Science | University of Texas at Austin | 2013 - 2015
Specialization: Distributed Systems & Machine Learning | GPA: 3.9/4.0
Thesis: "Optimizing Distributed Query Processing in Large-Scale Databases"

Bachelor of Engineering in Computer Science | Indian Institute of Technology | 2009 - 2013
GPA: 3.8/4.0 | Dean's List (all semesters)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CERTIFICATIONS & AWARDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ AWS Certified Solutions Architect - Professional (2023)
✓ Google Cloud Professional Cloud Architect (2022)
✓ Microsoft Certified: Azure Developer Associate (2021)
✓ Certified Kubernetes Administrator (CKA) (2020)
✓ "Top 1% Developer" - Stack Overflow (2019-2024)
✓ 1st Place - TechCrunch Hackathon San Francisco (2019)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OPEN SOURCE & SIDE PROJECTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• React-Query-Builder - NPM package with 50K+ weekly downloads (Maintainer)
• Next.js Boilerplate - Starter template with 5K+ GitHub stars (Creator)
• Contributor to: React.js, Node.js, TypeScript, Jest (100+ merged PRs)
• Tech Blog: alexkumar.io/blog - 50K+ monthly readers on web development topics

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LANGUAGES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

English (Native) | Spanish (Professional) | Hindi (Native) | Mandarin (Basic)
"""
    
    # Save as text file
    txt_path = SAMPLE_DIR / 'alex_kumar_complex.txt'
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(complex_content)
    print(f"✓ Created complex resume: alex_kumar_complex.txt")
    
    # Try to convert to PDF (if reportlab is available)
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        
        pdf_path = SAMPLE_DIR / 'alex_kumar_complex.pdf'
        doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        for line in complex_content.split('\n'):
            if line.strip():
                if '━' in line:  # Skip separator lines
                    story.append(Spacer(1, 0.1*inch))
                else:
                    para = Paragraph(line, styles['Normal'])
                    story.append(para)
            else:
                story.append(Spacer(1, 0.05*inch))
        
        doc.build(story)
        print(f"✓ Created complex resume PDF: alex_kumar_complex.pdf")
    except ImportError:
        print("ℹ PDF generation skipped (reportlab not available)")

def main():
    """Main function to download all sample resumes"""
    print("=" * 70)
    print("DOWNLOADING SAMPLE RESUMES FROM PUBLIC SOURCES")
    print("=" * 70)
    
    # Create complex test resume
    create_sample_complex_resume()
    
    # Try to download from GitHub
    try:
        download_github_resumes()
    except Exception as e:
        print(f"\n✗ GitHub downloads failed: {e}")
        print("You can download manually from the links in README.md")
    
    # Show manual download instructions
    download_overleaf_samples()
    
    print("\n" + "=" * 70)
    print("DOWNLOAD SUMMARY")
    print("=" * 70)
    
    # List downloaded files
    files = list(SAMPLE_DIR.glob('*'))
    if files:
        print(f"\nFiles in {SAMPLE_DIR}:")
        for f in sorted(files):
            if f.is_file():
                size_kb = f.stat().st_size / 1024
                print(f"  ✓ {f.name} ({size_kb:.1f} KB)")
    else:
        print("\nNo files downloaded yet.")
    
    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("\n1. Check the 'real_world' folder for downloaded resumes")
    print("2. Manually download additional resumes from Overleaf/Resume.io")
    print("3. (Optional) Add your own resume to the folder")
    print(f"4. Run resume parser on all files in: {SAMPLE_DIR}")
    print("\n" + "=" * 70)

if __name__ == '__main__':
    main()
