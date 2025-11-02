"""
Interactive Testing Tool for Manual Resume Validation
Helps test 100 resumes one-by-one with guided verification
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.resume_parser import ResumeParser
from src.ml.semantic_matcher import SemanticMatcher
from src.ml.quality_scorer import QualityScorer
from src.ml.experience_classifier import ExperienceClassifier

class InteractiveTester:
    """Interactive testing tool for manual validation"""
    
    def __init__(self, test_dir: str):
        self.test_dir = Path(test_dir)
        self.results_dir = project_root / "test_results" / "manual_testing"
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        print("🔧 Initializing components...")
        self.parser = ResumeParser()
        self.quality_scorer = QualityScorer()
        self.experience_classifier = ExperienceClassifier()
        
        # Load or create test log
        self.log_file = self.results_dir / f"test_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.current_batch = []
        self.stats = {
            'total_tested': 0,
            'components': {
                'parsing': {'success': 0, 'total': 0},
                'personal_info': {'correct': 0, 'total': 0},
                'skills': {'correct': 0, 'total': 0},
                'experience': {'correct': 0, 'total': 0},
                'education': {'correct': 0, 'total': 0},
                'quality': {'acceptable': 0, 'total': 0},
            }
        }
        
        print("✅ Interactive Testing Tool Ready!\n")
    
    def get_resume_files(self):
        """Get all resume files from test directory"""
        resumes = []
        for ext in ['*.pdf', '*.docx']:
            resumes.extend(self.test_dir.glob(f"**/{ext}"))
        return sorted(resumes)
    
    def display_header(self, resume_num: int, total: int, filename: str):
        """Display test header"""
        print("\n" + "="*80)
        print(f"📄 TESTING RESUME {resume_num}/{total}")
        print(f"📁 File: {filename}")
        print("="*80 + "\n")
    
    def test_resume(self, resume_path: Path, resume_num: int, total: int):
        """Test a single resume with guided verification"""
        
        self.display_header(resume_num, total, resume_path.name)
        
        result = {
            'resume_id': resume_path.stem,
            'filename': resume_path.name,
            'timestamp': datetime.now().isoformat(),
            'components': {}
        }
        
        try:
            # ========== COMPONENT 1: PARSING ==========
            print("🔍 STEP 1: PARSING")
            print("-" * 80)
            parsed = self.parser.parse(str(resume_path))
            
            if parsed and parsed.get('raw_text'):
                print(f"✅ Parsing: SUCCESS")
                print(f"📊 Text Length: {len(parsed['raw_text'])} characters")
                print(f"📄 Preview (first 200 chars):")
                print(parsed['raw_text'][:200] + "...")
                
                parse_ok = input("\n❓ Does the text look correct? (y/n): ").strip().lower() == 'y'
                result['components']['parsing'] = {
                    'success': parse_ok,
                    'text_length': len(parsed['raw_text'])
                }
                self.stats['components']['parsing']['total'] += 1
                if parse_ok:
                    self.stats['components']['parsing']['success'] += 1
            else:
                print("❌ Parsing: FAILED")
                result['components']['parsing'] = {'success': False, 'error': 'No text extracted'}
                self.stats['components']['parsing']['total'] += 1
                return result
            
            # ========== COMPONENT 2: PERSONAL INFO ==========
            print("\n" + "="*80)
            print("👤 STEP 2: PERSONAL INFORMATION")
            print("-" * 80)
            
            personal_info = parsed.get('personal_info', {})
            print(f"Name:     {personal_info.get('name', 'NOT FOUND')}")
            print(f"Email:    {personal_info.get('email', 'NOT FOUND')}")
            print(f"Phone:    {personal_info.get('phone', 'NOT FOUND')}")
            print(f"Location: {personal_info.get('location', 'NOT FOUND')}")
            print(f"LinkedIn: {personal_info.get('linkedin', 'NOT FOUND')}")
            print(f"GitHub:   {personal_info.get('github', 'NOT FOUND')}")
            
            print("\n📝 Please verify each field:")
            name_ok = input("  Is Name correct? (y/n/na): ").strip().lower()
            email_ok = input("  Is Email correct? (y/n/na): ").strip().lower()
            phone_ok = input("  Is Phone correct? (y/n/na): ").strip().lower()
            location_ok = input("  Is Location correct? (y/n/na): ").strip().lower()
            
            personal_checks = {
                'name': name_ok,
                'email': email_ok,
                'phone': phone_ok,
                'location': location_ok
            }
            
            correct_count = sum(1 for v in personal_checks.values() if v == 'y')
            total_count = sum(1 for v in personal_checks.values() if v != 'na')
            
            result['components']['personal_info'] = {
                'extracted': personal_info,
                'checks': personal_checks,
                'accuracy': correct_count / total_count if total_count > 0 else 0
            }
            
            self.stats['components']['personal_info']['total'] += total_count
            self.stats['components']['personal_info']['correct'] += correct_count
            
            # ========== COMPONENT 3: SKILLS ==========
            print("\n" + "="*80)
            print("💡 STEP 3: SKILLS EXTRACTION")
            print("-" * 80)
            
            skills = parsed.get('skills', {})
            all_skills = skills.get('all_skills', []) if isinstance(skills, dict) else []
            
            print(f"📊 Total Skills Found: {len(all_skills)}")
            if all_skills:
                print("🔹 Extracted Skills:")
                for i, skill in enumerate(all_skills[:20], 1):  # Show first 20
                    print(f"   {i}. {skill}")
                if len(all_skills) > 20:
                    print(f"   ... and {len(all_skills) - 20} more")
            
            print("\n📝 Manual Verification:")
            actual_count = input("  How many skills are ACTUALLY in the resume? (number): ").strip()
            try:
                actual_count = int(actual_count)
                recall = len(all_skills) / actual_count if actual_count > 0 else 0
                print(f"  📊 Recall: {recall*100:.1f}% ({len(all_skills)}/{actual_count})")
            except:
                recall = None
            
            false_positives = input("  How many extracted skills are WRONG? (number): ").strip()
            try:
                false_positives = int(false_positives)
                precision = (len(all_skills) - false_positives) / len(all_skills) if len(all_skills) > 0 else 0
                print(f"  📊 Precision: {precision*100:.1f}%")
            except:
                precision = None
            
            skill_quality = input("  Overall skill extraction quality (1-5): ").strip()
            
            result['components']['skills'] = {
                'extracted_count': len(all_skills),
                'actual_count': actual_count if isinstance(actual_count, int) else None,
                'false_positives': false_positives if isinstance(false_positives, int) else None,
                'recall': recall,
                'precision': precision,
                'quality_rating': skill_quality
            }
            
            if skill_quality in ['4', '5']:
                self.stats['components']['skills']['correct'] += 1
            self.stats['components']['skills']['total'] += 1
            
            # ========== COMPONENT 4: EXPERIENCE ==========
            print("\n" + "="*80)
            print("💼 STEP 4: WORK EXPERIENCE")
            print("-" * 80)
            
            experience = parsed.get('experience', [])
            print(f"📊 Work Experiences Found: {len(experience)}")
            
            for i, exp in enumerate(experience, 1):
                print(f"\n🔹 Experience #{i}:")
                print(f"   Company:  {exp.get('company', 'N/A')}")
                print(f"   Title:    {exp.get('title', 'N/A')}")
                print(f"   Duration: {exp.get('duration', 'N/A')}")
                print(f"   Dates:    {exp.get('start_date', 'N/A')} - {exp.get('end_date', 'Present' if exp.get('current') else 'N/A')}")
            
            exp_quality = input("\n  Experience extraction quality (1-5): ").strip()
            
            result['components']['experience'] = {
                'count': len(experience),
                'details': experience,
                'quality_rating': exp_quality
            }
            
            if exp_quality in ['4', '5']:
                self.stats['components']['experience']['correct'] += 1
            self.stats['components']['experience']['total'] += 1
            
            # ========== COMPONENT 5: EDUCATION ==========
            print("\n" + "="*80)
            print("🎓 STEP 5: EDUCATION")
            print("-" * 80)
            
            education = parsed.get('education', [])
            print(f"📊 Education Entries Found: {len(education)}")
            
            for i, edu in enumerate(education, 1):
                print(f"\n🔹 Education #{i}:")
                print(f"   Institution: {edu.get('institution', 'N/A')}")
                print(f"   Degree:      {edu.get('degree', 'N/A')}")
                print(f"   Field:       {edu.get('field', 'N/A')}")
                print(f"   Date:        {edu.get('date', 'N/A')}")
            
            edu_quality = input("\n  Education extraction quality (1-5): ").strip()
            
            result['components']['education'] = {
                'count': len(education),
                'details': education,
                'quality_rating': edu_quality
            }
            
            if edu_quality in ['4', '5']:
                self.stats['components']['education']['correct'] += 1
            self.stats['components']['education']['total'] += 1
            
            # ========== COMPONENT 6: EXPERIENCE CLASSIFICATION ==========
            print("\n" + "="*80)
            print("📊 STEP 6: EXPERIENCE LEVEL CLASSIFICATION")
            print("-" * 80)
            
            # Extract experience text
            exp_texts = []
            for exp in experience:
                if isinstance(exp, dict):
                    company = exp.get('company', '')
                    title = exp.get('title', '')
                    desc = exp.get('description', '')
                    exp_texts.append(f"{company} {title} {desc}")
            
            exp_text = " ".join(exp_texts)
            
            if exp_text.strip():
                level, confidence = self.experience_classifier.predict(exp_text)
                print(f"🎯 Classified as: {level} (confidence: {confidence:.2f})")
            else:
                level = "UNKNOWN"
                confidence = 0.0
                print("⚠️ No experience text to classify")
            
            manual_level = input("\n  What level would YOU classify this resume? (Entry/Mid/Senior/Expert): ").strip().title()
            
            level_match = (level.upper() == manual_level.upper())
            
            result['components']['experience_classification'] = {
                'system_classification': level,
                'confidence': confidence,
                'manual_classification': manual_level,
                'match': level_match
            }
            
            # ========== COMPONENT 7: QUALITY SCORING ==========
            print("\n" + "="*80)
            print("⭐ STEP 7: QUALITY SCORING")
            print("-" * 80)
            
            quality = self.quality_scorer.score_resume(parsed)
            print(f"📊 System Quality Score: {quality['overall_score']:.1f}/10")
            print("\nBreakdown:")
            for factor, score in quality['scores'].items():
                print(f"  {factor}: {score:.1f}/10")
            
            manual_score = input("\n  What score would YOU give (1-10)? ").strip()
            try:
                manual_score = float(manual_score)
                diff = abs(quality['overall_score'] - manual_score)
                print(f"  📊 Difference: {diff:.1f} points")
                acceptable = diff <= 2.0
            except:
                manual_score = None
                acceptable = False
            
            result['components']['quality'] = {
                'system_score': quality['overall_score'],
                'manual_score': manual_score,
                'acceptable': acceptable
            }
            
            if acceptable:
                self.stats['components']['quality']['acceptable'] += 1
            self.stats['components']['quality']['total'] += 1
            
            # ========== OVERALL ASSESSMENT ==========
            print("\n" + "="*80)
            print("✅ OVERALL ASSESSMENT")
            print("-" * 80)
            
            overall_rating = input("Overall system performance for this resume (1-5): ").strip()
            notes = input("Any notes or issues to record? (or press Enter): ").strip()
            
            result['overall_rating'] = overall_rating
            result['notes'] = notes
            
            print("\n✅ Resume test complete!")
            
        except Exception as e:
            print(f"\n❌ ERROR during testing: {str(e)}")
            result['error'] = str(e)
        
        # Save result
        self.current_batch.append(result)
        self.stats['total_tested'] += 1
        
        # Save after every resume
        self.save_results()
        
        return result
    
    def save_results(self):
        """Save test results to file"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump({
                'stats': self.stats,
                'results': self.current_batch,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)
    
    def display_stats(self):
        """Display current statistics"""
        print("\n" + "="*80)
        print("📊 TESTING STATISTICS")
        print("="*80)
        print(f"\n📈 Total Resumes Tested: {self.stats['total_tested']}")
        
        print("\n📋 Component Performance:")
        for component, data in self.stats['components'].items():
            if data['total'] > 0:
                success_rate = (data.get('correct', data.get('success', data.get('acceptable', 0))) / data['total']) * 100
                status = "🟢" if success_rate >= 90 else "🟡" if success_rate >= 75 else "🔴"
                print(f"  {status} {component.replace('_', ' ').title()}: {success_rate:.1f}% ({data.get('correct', data.get('success', data.get('acceptable', 0)))}/{data['total']})")
        
        print(f"\n💾 Results saved to: {self.log_file}")
        print("="*80 + "\n")
    
    def run_batch(self, start_idx=0, batch_size=None):
        """Run testing on a batch of resumes"""
        resumes = self.get_resume_files()
        
        if not resumes:
            print(f"❌ No resumes found in {self.test_dir}")
            return
        
        print(f"📂 Found {len(resumes)} resumes in {self.test_dir}")
        
        # Determine batch
        if batch_size:
            end_idx = min(start_idx + batch_size, len(resumes))
        else:
            end_idx = len(resumes)
        
        batch_resumes = resumes[start_idx:end_idx]
        
        print(f"🎯 Testing resumes {start_idx+1} to {end_idx} ({len(batch_resumes)} resumes)")
        
        for i, resume_path in enumerate(batch_resumes, start=start_idx+1):
            self.test_resume(resume_path, i, len(resumes))
            
            # Show stats every 10 resumes
            if i % 10 == 0:
                self.display_stats()
                
                cont = input("Continue to next batch? (y/n): ").strip().lower()
                if cont != 'y':
                    print("⏸️ Testing paused. You can resume later.")
                    break
        
        # Final stats
        self.display_stats()
        print("🎉 Testing session complete!")


def main():
    """Main entry point"""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║   📋 INTERACTIVE RESUME TESTING TOOL                       ║
    ║   Manual validation for 100 resumes                        ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    # Get test directory
    default_dir = project_root / "data" / "testing_resumes"
    
    test_dir = input(f"Enter test directory path (or press Enter for {default_dir}): ").strip()
    if not test_dir:
        test_dir = default_dir
    
    test_dir = Path(test_dir)
    
    if not test_dir.exists():
        print(f"❌ Directory not found: {test_dir}")
        create = input("Create this directory? (y/n): ").strip().lower()
        if create == 'y':
            test_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {test_dir}")
            print(f"📥 Please add resume files to {test_dir} and run this script again.")
        return
    
    # Initialize tester
    tester = InteractiveTester(test_dir)
    
    # Ask for batch size
    print("\n⚙️ Testing Options:")
    print("  1. Test all resumes")
    print("  2. Test in batches of 10")
    print("  3. Test in batches of 20")
    print("  4. Custom batch size")
    
    choice = input("\nYour choice (1-4): ").strip()
    
    if choice == '1':
        tester.run_batch()
    elif choice == '2':
        tester.run_batch(batch_size=10)
    elif choice == '3':
        tester.run_batch(batch_size=20)
    elif choice == '4':
        batch_size = int(input("Enter batch size: ").strip())
        tester.run_batch(batch_size=batch_size)
    else:
        print("Invalid choice. Testing all resumes.")
        tester.run_batch()


if __name__ == "__main__":
    main()
