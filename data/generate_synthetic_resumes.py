"""
Generate Synthetic Resume Dataset
Creates hundreds of realistic test resumes with varied content
Perfect for testing, training, and development
"""

import random
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Data templates for generating realistic resumes
FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "David", "Barbara", "William", "Elizabeth", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Christopher", "Karen", "Daniel", "Lisa", "Matthew", "Nancy",
    "Anthony", "Betty", "Mark", "Margaret", "Donald", "Sandra", "Steven", "Ashley",
    "Emily", "Sophia", "Isabella", "Mia", "Charlotte", "Amelia", "Harper", "Evelyn",
    "Aiden", "Lucas", "Mason", "Ethan", "Logan", "Alexander", "Oliver", "Elijah",
    "Priya", "Raj", "Wei", "Ming", "Carlos", "Maria", "Ahmed", "Fatima"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Thompson", "White",
    "Harris", "Clark", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
    "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green", "Adams",
    "Chen", "Kumar", "Patel", "Khan", "Singh", "Ali", "Wang", "Liu", "Zhang"
]

JOB_TITLES = {
    "software": [
        "Software Engineer", "Senior Software Developer", "Full Stack Developer",
        "Backend Engineer", "Frontend Developer", "DevOps Engineer", "Cloud Architect",
        "Software Development Manager", "Principal Engineer", "Lead Developer"
    ],
    "data": [
        "Data Scientist", "Machine Learning Engineer", "Data Analyst", "AI Researcher",
        "Senior Data Engineer", "ML Ops Engineer", "Analytics Manager", "Research Scientist",
        "Data Architect", "Business Intelligence Analyst"
    ],
    "product": [
        "Product Manager", "Senior Product Manager", "Product Owner", "Technical Product Manager",
        "Director of Product", "Product Strategy Lead", "Growth Product Manager",
        "Associate Product Manager", "VP of Product", "Chief Product Officer"
    ],
    "design": [
        "UX Designer", "UI/UX Designer", "Product Designer", "Senior UX Researcher",
        "Design Lead", "Creative Director", "Visual Designer", "Interaction Designer"
    ],
    "business": [
        "Business Analyst", "Strategy Consultant", "Operations Manager", "Project Manager",
        "Account Manager", "Sales Engineer", "Marketing Manager", "Financial Analyst"
    ]
}

SKILLS = {
    "software": [
        "Python", "Java", "JavaScript", "TypeScript", "C++", "Go", "Rust", "Ruby",
        "React", "Angular", "Vue.js", "Node.js", "Django", "Flask", "Spring Boot",
        "Docker", "Kubernetes", "AWS", "Azure", "GCP", "CI/CD", "Git", "SQL", "NoSQL",
        "Microservices", "REST API", "GraphQL", "MongoDB", "PostgreSQL", "Redis"
    ],
    "data": [
        "Python", "R", "SQL", "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy",
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "Statistics",
        "A/B Testing", "Data Visualization", "Tableau", "Power BI", "Spark", "Hadoop",
        "MLOps", "Feature Engineering", "Model Deployment", "Time Series", "Keras"
    ],
    "product": [
        "Product Strategy", "Roadmap Planning", "User Research", "A/B Testing", "Analytics",
        "Jira", "Agile", "Scrum", "SQL", "Data Analysis", "Wireframing", "Figma",
        "Product Marketing", "Go-to-Market", "Stakeholder Management", "OKRs", "KPIs"
    ],
    "design": [
        "Figma", "Sketch", "Adobe XD", "Photoshop", "Illustrator", "InVision", "Prototyping",
        "User Research", "Wireframing", "Design Systems", "HTML/CSS", "Responsive Design",
        "Accessibility", "Information Architecture", "Usability Testing", "Typography"
    ],
    "business": [
        "Excel", "SQL", "Tableau", "PowerPoint", "Salesforce", "Market Research",
        "Financial Modeling", "Project Management", "Agile", "Strategic Planning",
        "Stakeholder Management", "Business Intelligence", "CRM", "Data Analysis"
    ]
}

COMPANIES = [
    "Google", "Meta", "Amazon", "Microsoft", "Apple", "Netflix", "Tesla", "SpaceX",
    "Salesforce", "Oracle", "IBM", "Intel", "Adobe", "Uber", "Airbnb", "LinkedIn",
    "Twitter", "Spotify", "Stripe", "Square", "Coinbase", "Robinhood", "DoorDash",
    "Instacart", "Shopify", "Zoom", "Slack", "Atlassian", "ServiceNow", "Workday",
    "Tech Startup Inc", "Innovation Labs", "Digital Solutions Corp", "Cloud Systems LLC"
]

UNIVERSITIES = [
    "Stanford University", "MIT", "Carnegie Mellon University", "UC Berkeley",
    "Georgia Tech", "University of Washington", "UT Austin", "University of Michigan",
    "Cornell University", "Columbia University", "Harvard University", "Yale University",
    "Princeton University", "Caltech", "UCLA", "USC", "UCSD", "Northwestern University",
    "University of Illinois", "Purdue University", "Penn State", "University of Wisconsin"
]

DEGREES = [
    "Bachelor of Science in Computer Science",
    "Master of Science in Computer Science",
    "Bachelor of Engineering in Software Engineering",
    "Master of Science in Data Science",
    "Bachelor of Science in Information Technology",
    "Master of Business Administration",
    "Bachelor of Science in Mathematics",
    "PhD in Computer Science",
    "Bachelor of Science in Electrical Engineering"
]


def generate_resume_data(category: str = "software") -> dict:
    """Generate realistic resume data"""
    
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    
    years_exp = random.randint(2, 15)
    
    # Ensure we don't sample more skills than available
    available_skills = len(SKILLS[category])
    num_skills = min(random.randint(8, 15), available_skills)
    
    data = {
        "name": f"{first_name} {last_name}",
        "email": f"{first_name.lower()}.{last_name.lower()}@email.com",
        "phone": f"({random.randint(100, 999)}) {random.randint(100, 999)}-{random.randint(1000, 9999)}",
        "location": random.choice(["San Francisco, CA", "New York, NY", "Seattle, WA", "Austin, TX", "Boston, MA"]),
        "linkedin": f"linkedin.com/in/{first_name.lower()}{last_name.lower()}",
        "github": f"github.com/{first_name.lower()}{last_name[0].lower()}",
        "years_exp": years_exp,
        "title": random.choice(JOB_TITLES[category]),
        "skills": random.sample(SKILLS[category], k=num_skills),
        "education": {
            "degree": random.choice(DEGREES),
            "university": random.choice(UNIVERSITIES),
            "year": random.randint(2010, 2023),
            "gpa": round(random.uniform(3.5, 4.0), 2)
        },
        "experience": []
    }
    
    # Generate 2-4 work experiences
    for i in range(random.randint(2, 4)):
        exp = {
            "title": random.choice(JOB_TITLES[category]),
            "company": random.choice(COMPANIES),
            "years": f"{random.randint(1, 4)} years",
            "achievements": [
                f"Led team of {random.randint(3, 12)} engineers in developing new features",
                f"Improved system performance by {random.randint(20, 80)}%",
                f"Reduced costs by ${random.randint(10, 500)}K annually",
                f"Launched {random.randint(2, 8)} major features serving {random.randint(100, 5000)}K+ users"
            ][:random.randint(2, 4)]
        }
        data["experience"].append(exp)
    
    return data


def create_pdf_resume(data: dict, output_path: Path):
    """Create PDF resume using ReportLab"""
    
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    styles = getSampleStyleSheet()
    story = []
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=6,
        alignment=TA_CENTER
    )
    
    # Contact style
    contact_style = ParagraphStyle(
        'Contact',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#555555'),
        alignment=TA_CENTER
    )
    
    # Section heading
    section_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=6,
        spaceBefore=12,
        borderWidth=1,
        borderColor=colors.HexColor('#2C3E50'),
        borderPadding=5
    )
    
    # Name
    story.append(Paragraph(data['name'].upper(), title_style))
    
    # Contact info
    contact = f"{data['email']} | {data['phone']} | {data['location']}"
    story.append(Paragraph(contact, contact_style))
    story.append(Paragraph(f"{data['linkedin']} | {data['github']}", contact_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Summary
    story.append(Paragraph("PROFESSIONAL SUMMARY", section_style))
    summary = f"{data['title']} with {data['years_exp']}+ years of experience. "
    summary += f"Skilled in {', '.join(data['skills'][:3])}."
    story.append(Paragraph(summary, styles['Normal']))
    story.append(Spacer(1, 0.1*inch))
    
    # Experience
    story.append(Paragraph("PROFESSIONAL EXPERIENCE", section_style))
    for exp in data['experience']:
        story.append(Paragraph(f"<b>{exp['title']}</b> | {exp['company']} | {exp['years']}", styles['Normal']))
        for achievement in exp['achievements']:
            story.append(Paragraph(f"• {achievement}", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
    
    # Skills
    story.append(Paragraph("TECHNICAL SKILLS", section_style))
    skills_text = ", ".join(data['skills'])
    story.append(Paragraph(skills_text, styles['Normal']))
    story.append(Spacer(1, 0.1*inch))
    
    # Education
    story.append(Paragraph("EDUCATION", section_style))
    edu = data['education']
    story.append(Paragraph(f"<b>{edu['degree']}</b>", styles['Normal']))
    story.append(Paragraph(f"{edu['university']} | Graduated: {edu['year']} | GPA: {edu['gpa']}", styles['Normal']))
    
    # Build PDF
    doc.build(story)


def generate_dataset(num_resumes: int = 100, output_dir: str = "data/sample_resumes/synthetic_dataset"):
    """Generate synthetic resume dataset"""
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"\n{'='*80}")
    logger.info(f"GENERATING SYNTHETIC RESUME DATASET")
    logger.info(f"{'='*80}\n")
    logger.info(f"Creating {num_resumes} resumes...")
    logger.info(f"Output: {output_path.absolute()}\n")
    
    categories = list(JOB_TITLES.keys())
    
    for i in range(num_resumes):
        category = random.choice(categories)
        data = generate_resume_data(category)
        
        filename = f"{data['name'].replace(' ', '_').lower()}_{category}_{i+1:03d}.pdf"
        file_path = output_path / filename
        
        try:
            create_pdf_resume(data, file_path)
            
            if (i + 1) % 10 == 0:
                logger.info(f"✓ Created {i+1}/{num_resumes} resumes...")
        
        except Exception as e:
            logger.error(f"✗ Failed to create {filename}: {e}")
            continue
    
    logger.info(f"\n{'='*80}")
    logger.info(f"✅ GENERATION COMPLETE!")
    logger.info(f"{'='*80}")
    logger.info(f"Created {num_resumes} synthetic resumes")
    logger.info(f"Location: {output_path.absolute()}")
    logger.info(f"\nNext step: Test with these resumes!")
    logger.info(f"  python test_parser.py")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("SYNTHETIC RESUME DATASET GENERATOR")
    print("="*80)
    print("\n⚙️  This will generate realistic test resumes with:")
    print("   • Varied job titles (Software, Data, Product, Design, Business)")
    print("   • Random names, skills, experience, education")
    print("   • Professional PDF formatting")
    print("\n" + "="*80)
    
    num = input("\n📝 How many resumes to generate? (default: 100): ").strip()
    num_resumes = int(num) if num.isdigit() else 100
    
    generate_dataset(num_resumes=num_resumes)
