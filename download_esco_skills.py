"""
Download ESCO Skills Taxonomy
ESCO = European Skills, Competences, Qualifications and Occupations
Official EU skill database with ~13,890 skills
"""
import requests
import csv
import json
from pathlib import Path

print("📥 Downloading ESCO Skills Taxonomy...")
print("=" * 60)

# ESCO provides CSV downloads
# Using the skills taxonomy CSV
ESCO_CSV_URL = "https://ec.europa.eu/esco/api/resource/download?type=skill&language=en&format=csv"

try:
    response = requests.get(ESCO_CSV_URL, timeout=60)
    response.raise_for_status()
    
    # Save raw CSV
    csv_path = Path('data/skills/esco_skills.csv')
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(csv_path, 'wb') as f:
        f.write(response.content)
    
    print(f"✅ Downloaded ESCO CSV to: {csv_path}")
    print(f"   Size: {len(response.content) / 1024 / 1024:.2f} MB")
    
except Exception as e:
    print(f"⚠️  Official API failed: {e}")
    print("📝 Using alternative approach: Common skill taxonomy")
    
    # Fallback: Create a comprehensive skill taxonomy from multiple sources
    # This includes common technical, soft, and domain skills
    skills = {
        # Programming Languages & Frameworks
        "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Ruby", "PHP", "Swift", "Kotlin",
        "Go", "Rust", "Scala", "R", "MATLAB", "Perl", "Shell", "Bash",
        "React", "Angular", "Vue.js", "Node.js", "Django", "Flask", "Spring", "Express.js",
        "React Native", "Flutter", "Xamarin", "jQuery", "Bootstrap", "Tailwind CSS",
        
        # Databases
        "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "Oracle", "SQL Server",
        "SQLite", "Cassandra", "DynamoDB", "Firebase", "Elasticsearch", "Neo4j",
        
        # Cloud & DevOps
        "AWS", "Azure", "Google Cloud", "GCP", "Docker", "Kubernetes", "Jenkins",
        "CI/CD", "GitLab", "GitHub Actions", "Terraform", "Ansible", "Chef", "Puppet",
        "Microservices", "Serverless", "Lambda", "Cloud Computing", "DevOps",
        
        # Data Science & ML
        "Machine Learning", "Deep Learning", "Neural Networks", "TensorFlow", "PyTorch",
        "Scikit-learn", "Keras", "NLP", "Computer Vision", "Data Science", "Data Analysis",
        "Statistics", "Pandas", "NumPy", "Matplotlib", "Tableau", "Power BI",
        "Big Data", "Hadoop", "Spark", "Kafka", "ETL", "Data Warehousing",
        
        # Microsoft Office & Tools
        "Excel", "Word", "PowerPoint", "Outlook", "Microsoft Office", "MS Office",
        "Microsoft Office Suite", "Access", "SharePoint", "OneDrive", "Teams",
        "Google Workspace", "Google Sheets", "Google Docs", "Slack",
        
        # Design & Creative
        "Photoshop", "Illustrator", "InDesign", "Figma", "Sketch", "Adobe XD",
        "UI/UX Design", "Graphic Design", "Web Design", "Video Editing", "AutoCAD",
        
        # Project Management & Methodologies
        "Project Management", "Agile", "Scrum", "Kanban", "Waterfall", "Jira",
        "Trello", "Asana", "Microsoft Project", "PMP", "Six Sigma", "Lean",
        
        # Soft Skills
        "Communication", "Leadership", "Teamwork", "Problem Solving", "Critical Thinking",
        "Time Management", "Organization", "Analytical", "Attention to Detail",
        "Decision Making", "Conflict Resolution", "Negotiation", "Presentation",
        "Interpersonal Skills", "Adaptability", "Creativity", "Collaboration",
        "Strategic Planning", "Mentoring", "Coaching", "Public Speaking",
        
        # Business & Finance
        "Accounting", "Financial Analysis", "Budgeting", "Forecasting", "Financial Modeling",
        "QuickBooks", "SAP", "ERP", "CRM", "Salesforce", "HubSpot", "Oracle ERP",
        "Business Analysis", "Market Research", "Business Development", "Sales",
        "Marketing", "Digital Marketing", "SEO", "SEM", "Social Media Marketing",
        
        # Security
        "Cybersecurity", "Information Security", "Network Security", "Penetration Testing",
        "Ethical Hacking", "CISSP", "Security+", "Firewall", "VPN", "Encryption",
        
        # Networking
        "Networking", "TCP/IP", "DNS", "DHCP", "LAN", "WAN", "Routing", "Switching",
        "Cisco", "CCNA", "Network Administration",
        
        # Web Technologies
        "HTML", "CSS", "REST API", "GraphQL", "JSON", "XML", "AJAX", "WebSockets",
        "OAuth", "JWT", "API Development", "Web Services",
        
        # Testing & Quality
        "Quality Assurance", "QA", "Testing", "Unit Testing", "Integration Testing",
        "Selenium", "Jest", "Pytest", "JUnit", "Test Automation", "Manual Testing",
        
        # Operating Systems
        "Linux", "Unix", "Windows", "macOS", "Ubuntu", "Red Hat", "CentOS",
        
        # Version Control
        "Git", "GitHub", "GitLab", "Bitbucket", "SVN", "Version Control",
        
        # Languages (Human)
        "English", "Spanish", "French", "German", "Chinese", "Japanese", "Arabic",
        "Portuguese", "Russian", "Italian", "Korean", "Dutch", "Swedish",
        
        # Industry-Specific
        "Healthcare", "HIPAA", "FDA Compliance", "Clinical Research", "Medical Coding",
        "Legal Research", "Contract Law", "Litigation", "Compliance",
        "Manufacturing", "Supply Chain", "Logistics", "Inventory Management",
        "Retail", "Customer Service", "Point of Sale", "POS", "Merchandising",
        "Real Estate", "Property Management", "Leasing",
        "Education", "Curriculum Development", "Instructional Design", "E-Learning",
        
        # Certifications (common)
        "PMP", "CISSP", "AWS Certified", "Azure Certified", "Google Certified",
        "Certified Scrum Master", "CSM", "CEH", "CompTIA A+", "CompTIA Security+",
    }
    
    # Expand with variations
    expanded_skills = set(skills)
    
    # Add lowercase and title case variations
    for skill in list(skills):
        expanded_skills.add(skill.lower())
        expanded_skills.add(skill.title())
        expanded_skills.add(skill.upper())
    
    # Convert to list and sort
    skills_list = sorted(list(expanded_skills))
    
    # Save as JSON
    output_data = {
        "source": "Curated Technical & Business Skills Taxonomy",
        "version": "1.0",
        "total_skills": len(skills_list),
        "categories": [
            "Programming", "Databases", "Cloud/DevOps", "Data Science/ML",
            "Microsoft Office", "Design", "Project Management", "Soft Skills",
            "Business/Finance", "Security", "Networking", "Web Technologies",
            "Testing/QA", "Operating Systems", "Version Control", "Languages",
            "Industry-Specific", "Certifications"
        ],
        "skills": skills_list
    }
    
    json_path = Path('data/skills/validated_skills.json')
    json_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created curated skills taxonomy: {json_path}")
    print(f"   Total skills: {len(skills_list):,}")
    print(f"   Categories: {len(output_data['categories'])}")
    print()
    print("📋 Sample skills:")
    for i, skill in enumerate(skills_list[:20], 1):
        print(f"   {i}. {skill}")
    print(f"   ... and {len(skills_list) - 20:,} more")

print("\n✅ Skill taxonomy ready for validation!")
