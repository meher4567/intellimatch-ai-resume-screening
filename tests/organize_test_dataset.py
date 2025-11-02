"""
Resume Dataset Organizer
Helps organize downloaded resumes into structured batches
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

class ResumeOrganizer:
    """Organizes resumes into batches by category"""
    
    def __init__(self, source_dir: str, target_base: str = "data/testing_resumes"):
        self.source_dir = Path(source_dir)
        self.target_base = Path(target_base)
        
        # Define batch structure
        self.batches = {
            'batch_001_software': {
                'count': 20,
                'description': 'Software Engineering resumes'
            },
            'batch_002_datascience': {
                'count': 15,
                'description': 'Data Science/ML resumes'
            },
            'batch_003_academic': {
                'count': 15,
                'description': 'Academic/Research CVs'
            },
            'batch_004_product': {
                'count': 10,
                'description': 'Product Management resumes'
            },
            'batch_005_design': {
                'count': 10,
                'description': 'Design/Creative resumes'
            },
            'batch_006_finance': {
                'count': 10,
                'description': 'Finance/Consulting resumes'
            },
            'batch_007_healthcare': {
                'count': 10,
                'description': 'Healthcare/Medical resumes'
            },
            'batch_008_other': {
                'count': 10,
                'description': 'Other industries'
            }
        }
    
    def setup_structure(self):
        """Create batch directories"""
        print("📁 Setting up directory structure...\n")
        
        for batch_name, info in self.batches.items():
            batch_dir = self.target_base / batch_name
            batch_dir.mkdir(parents=True, exist_ok=True)
            
            # Create README in each batch
            readme = batch_dir / "README.md"
            readme.write_text(f"""# {batch_name.replace('_', ' ').title()}

**Target Count**: {info['count']} resumes
**Description**: {info['description']}

## Instructions:
1. Download {info['count']} resumes matching this category
2. Name them descriptively (e.g., `john_doe_senior_swe.pdf`)
3. Place them in this directory

## Naming Convention:
- Use lowercase with underscores
- Include key info: name_level_role.pdf
- Examples:
  - sarah_chen_senior_data_scientist.pdf
  - michael_ross_entry_frontend_dev.pdf
  - jane_doe_phd_ml_researcher.pdf

## Progress:
- [ ] Downloaded {info['count']} resumes
- [ ] Named appropriately
- [ ] Ready for testing
""")
            
            print(f"✅ Created: {batch_dir}")
        
        # Create master metadata file
        metadata = {
            'created': datetime.now().isoformat(),
            'total_target': 100,
            'batches': self.batches,
            'status': 'setup_complete'
        }
        
        import json
        metadata_file = self.target_base / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n✅ Setup complete! Directories created at: {self.target_base}")
    
    def organize_existing(self):
        """Organize resumes from source directory into batches"""
        if not self.source_dir.exists():
            print(f"❌ Source directory not found: {self.source_dir}")
            return
        
        # Get all resume files
        resumes = []
        for ext in ['*.pdf', '*.docx']:
            resumes.extend(self.source_dir.glob(f"**/{ext}"))
        
        if not resumes:
            print(f"❌ No resumes found in {self.source_dir}")
            return
        
        print(f"📂 Found {len(resumes)} resumes in {self.source_dir}\n")
        print("🔄 Interactive Organization Mode")
        print("="*60 + "\n")
        
        for i, resume in enumerate(resumes, 1):
            print(f"📄 Resume {i}/{len(resumes)}: {resume.name}")
            print("\nAvailable batches:")
            for j, (batch_name, info) in enumerate(self.batches.items(), 1):
                print(f"  {j}. {batch_name} - {info['description']}")
            
            choice = input("\nSelect batch (1-8) or 's' to skip: ").strip()
            
            if choice == 's':
                print("⏭️ Skipped\n")
                continue
            
            try:
                batch_idx = int(choice) - 1
                batch_name = list(self.batches.keys())[batch_idx]
                target_dir = self.target_base / batch_name
                
                # Ask for new name
                current_name = resume.stem
                new_name = input(f"New filename (or Enter to keep '{current_name}'): ").strip()
                
                if not new_name:
                    new_name = current_name
                
                # Ensure proper extension
                new_name = new_name.replace(' ', '_').lower()
                if not new_name.endswith(resume.suffix):
                    new_name += resume.suffix
                
                target_path = target_dir / new_name
                
                # Copy file
                shutil.copy2(resume, target_path)
                print(f"✅ Copied to: {target_path}\n")
                
            except (ValueError, IndexError):
                print("❌ Invalid choice, skipped\n")
        
        print("🎉 Organization complete!")
    
    def check_progress(self):
        """Check how many resumes are in each batch"""
        print("\n📊 TESTING DATASET PROGRESS")
        print("="*60 + "\n")
        
        total = 0
        for batch_name, info in self.batches.items():
            batch_dir = self.target_base / batch_name
            
            if batch_dir.exists():
                files = list(batch_dir.glob("*.pdf")) + list(batch_dir.glob("*.docx"))
                count = len(files)
                total += count
                target = info['count']
                percentage = (count / target) * 100
                
                status = "✅" if count >= target else "⏳"
                print(f"{status} {batch_name}")
                print(f"   Progress: {count}/{target} ({percentage:.0f}%)")
                print(f"   Files: {', '.join([f.name for f in files[:3]])}")
                if len(files) > 3:
                    print(f"          ... and {len(files)-3} more")
                print()
        
        print(f"📈 Total: {total}/100 resumes ({(total/100)*100:.0f}%)")
        
        if total >= 100:
            print("\n🎉 Dataset complete! Ready for testing!")
        else:
            print(f"\n⏳ Need {100-total} more resumes to reach 100")


def print_download_guide():
    """Print guide for downloading resumes"""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║   📥 RESUME DOWNLOAD GUIDE                                 ║
    ╚════════════════════════════════════════════════════════════╝
    
    🎯 GOAL: Download 100 diverse, real resumes
    
    📍 WHERE TO FIND RESUMES:
    
    1. Overleaf Gallery (PDF)
       🔗 https://www.overleaf.com/gallery/tagged/cv
       🔗 https://www.overleaf.com/gallery/tagged/resume
       - Click on templates
       - Download PDF directly
       - High-quality LaTeX resumes
    
    2. GitHub Resume Repositories
       🔗 https://github.com/topics/resume-template
       🔗 https://github.com/search?q=resume+pdf
       - Search: "resume template", "cv latex"
       - Clone repos with sample PDFs
       - Many real examples
    
    3. RenderCV Examples
       🔗 https://github.com/sinaatalay/rendercv
       - Excellent resume generator
       - Sample outputs available
    
    4. Reddit Resume Reviews
       🔗 r/resumes
       🔗 r/EngineeringResumes
       - Public resume reviews
       - Ask permission if needed
    
    5. Academic CV Collections
       🔗 University career sites
       🔗 Faculty CV pages (public)
       - Usually longer, detailed
    
    ⚙️ DOWNLOAD TIPS:
    
    ✅ Ensure diversity:
       - Different industries (tech, finance, healthcare, etc.)
       - Different levels (entry, mid, senior, expert)
       - Different formats (1-column, 2-column, creative)
    
    ✅ Name files descriptively:
       - Format: firstname_lastname_level_role.pdf
       - Example: john_doe_senior_software_engineer.pdf
    
    ✅ Verify quality:
       - Readable text (not scanned images)
       - Complete information
       - Professional formatting
    
    ⚠️ LEGAL/ETHICAL:
       - Only use publicly available resumes
       - Don't use copyrighted content without permission
       - Remove/anonymize if needed for privacy
    
    📊 TARGET DISTRIBUTION:
       - 20 Software Engineering
       - 15 Data Science/ML
       - 15 Academic/Research
       - 10 Product Management
       - 10 Design/Creative
       - 10 Finance/Consulting
       - 10 Healthcare/Medical
       - 10 Other industries
    
    🚀 ONCE DOWNLOADED:
       1. Run this script to organize them
       2. Use interactive_testing_tool.py to test
       3. Document results
       4. Make improvements
    
    ════════════════════════════════════════════════════════════
    """)


def main():
    """Main entry point"""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║   📁 RESUME DATASET ORGANIZER                              ║
    ║   Prepare 100 resumes for comprehensive testing           ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    print("\n⚙️ What would you like to do?")
    print("  1. Setup directory structure (first time)")
    print("  2. Organize existing resumes into batches")
    print("  3. Check progress")
    print("  4. Show download guide")
    print("  5. Exit")
    
    choice = input("\nYour choice (1-5): ").strip()
    
    if choice == '1':
        target = input("\nEnter target directory (or Enter for 'data/testing_resumes'): ").strip()
        if not target:
            target = "data/testing_resumes"
        
        organizer = ResumeOrganizer("", target)
        organizer.setup_structure()
        
        print("\n📝 Next steps:")
        print("1. Download resumes following the guide")
        print("2. Place them in the appropriate batch directories")
        print("3. Run option 3 to check progress")
        
    elif choice == '2':
        source = input("\nEnter source directory with downloaded resumes: ").strip()
        target = input("Enter target directory (or Enter for 'data/testing_resumes'): ").strip()
        
        if not target:
            target = "data/testing_resumes"
        
        organizer = ResumeOrganizer(source, target)
        organizer.organize_existing()
        
    elif choice == '3':
        target = input("\nEnter target directory (or Enter for 'data/testing_resumes'): ").strip()
        if not target:
            target = "data/testing_resumes"
        
        organizer = ResumeOrganizer("", target)
        organizer.check_progress()
        
    elif choice == '4':
        print_download_guide()
        
    elif choice == '5':
        print("👋 Goodbye!")
        return
    
    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    main()
