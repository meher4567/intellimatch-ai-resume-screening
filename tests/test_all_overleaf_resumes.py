"""
Comprehensive Testing of All Overleaf Template Resumes
Tests section extraction, parsing quality, and identifies issues
"""

import os
from pathlib import Path
from src.services.resume_parser import ResumeParser
import traceback

print("=" * 100)
print("🧪 COMPREHENSIVE TESTING - OVERLEAF TEMPLATE RESUMES")
print("=" * 100)

# Get all PDF files from overleaf_templates folder
overleaf_dir = Path("data/sample_resumes/overleaf_templates")
resume_files = sorted(list(overleaf_dir.glob("*.pdf")))

print(f"\n📂 Found {len(resume_files)} resume files to test")
print("=" * 100)

# Initialize parser
parser = ResumeParser(
    detect_sections=True,
    extract_contact=True,
    extract_name=True,
    assess_quality=True
)

# Track statistics
total_resumes = len(resume_files)
successful_parses = 0
failed_parses = 0
issues_found = []
all_results = []

# Test each resume
for i, resume_file in enumerate(resume_files, 1):
    resume_name = resume_file.name
    
    print(f"\n{'=' * 100}")
    print(f"📄 TEST {i}/{total_resumes}: {resume_name}")
    print('=' * 100)
    
    try:
        # Parse resume
        result = parser.parse(str(resume_file))
        
        if not result.get('success'):
            print(f"❌ PARSING FAILED: {result.get('error')}")
            failed_parses += 1
            issues_found.append({
                'resume': resume_name,
                'issue': 'Parsing failed',
                'details': result.get('error')
            })
            continue
        
        successful_parses += 1
        
        # Extract key information
        text = result.get('text', '')
        name = result.get('name')
        contact = result.get('contact_info', {})
        sections = result.get('sections', {})
        quality = result.get('quality', {})
        
        # Display results
        print(f"\n✅ Parsing Successful")
        print(f"   Characters: {len(text):,}")
        print(f"   Words: {result.get('word_count', 0):,}")
        print(f"   Quality Score: {quality.get('overall_score', 0):.1f}/100")
        
        # Name extraction
        if name:
            print(f"\n👤 Name: {name}")
        else:
            print(f"\n⚠️  Name: NOT DETECTED")
            issues_found.append({
                'resume': resume_name,
                'issue': 'Name not detected',
                'details': 'Name extraction failed'
            })
        
        # Contact information
        print(f"\n📧 Contact Info:")
        emails = contact.get('emails', [])
        phones = contact.get('phones', [])
        linkedin = contact.get('linkedin')
        github = contact.get('github')
        
        print(f"   Email: {'✅ ' + emails[0] if emails else '❌ Not found'}")
        print(f"   Phone: {'✅ ' + phones[0] if phones else '❌ Not found'}")
        print(f"   LinkedIn: {'✅ ' + linkedin if linkedin else '❌ Not found'}")
        print(f"   GitHub: {'✅ ' + github if github else '❌ Not found'}")
        
        if not emails:
            issues_found.append({
                'resume': resume_name,
                'issue': 'Email not detected',
                'details': 'Contact extraction issue'
            })
        
        # Sections detected
        print(f"\n📂 Sections Detected ({len(sections)}):")
        
        critical_sections = ['experience', 'education', 'skills']
        section_status = {}
        
        for section_name in critical_sections:
            if section_name in sections:
                section = sections[section_name]
                content_len = len(section.get('content', ''))
                confidence = section.get('confidence', 0)
                
                if content_len > 0:
                    print(f"   ✅ {section_name.upper()}: {content_len} chars (confidence: {confidence:.0%})")
                    section_status[section_name] = 'ok'
                else:
                    print(f"   ⚠️  {section_name.upper()}: EMPTY CONTENT (confidence: {confidence:.0%})")
                    section_status[section_name] = 'empty'
                    issues_found.append({
                        'resume': resume_name,
                        'issue': f'{section_name.capitalize()} section empty',
                        'details': f'Section detected but has 0 content'
                    })
            else:
                print(f"   ❌ {section_name.upper()}: NOT DETECTED")
                section_status[section_name] = 'missing'
                issues_found.append({
                    'resume': resume_name,
                    'issue': f'{section_name.capitalize()} section missing',
                    'details': f'Critical section not found'
                })
        
        # Show all detected sections
        other_sections = [s for s in sections.keys() if s not in critical_sections]
        if other_sections:
            print(f"\n   📋 Other sections: {', '.join(other_sections)}")
        
        # Check for projects
        if 'projects' in sections:
            project_content = sections['projects'].get('content', '')
            if len(project_content) > 0:
                print(f"   ✅ PROJECTS: {len(project_content)} chars")
            else:
                print(f"   ⚠️  PROJECTS: Section found but EMPTY")
                issues_found.append({
                    'resume': resume_name,
                    'issue': 'Projects section empty',
                    'details': 'Projects header found but no content'
                })
        
        # Quality issues
        quality_issues = quality.get('issues', [])
        if quality_issues:
            print(f"\n⚠️  Quality Issues ({len(quality_issues)}):")
            for issue in quality_issues[:3]:
                print(f"   • {issue}")
        
        # Store result for summary
        all_results.append({
            'name': resume_name,
            'success': True,
            'quality_score': quality.get('overall_score', 0),
            'sections_found': len(sections),
            'has_name': bool(name),
            'has_email': bool(emails),
            'section_status': section_status,
            'char_count': len(text)
        })
        
    except Exception as e:
        print(f"\n❌ EXCEPTION OCCURRED:")
        print(f"   Error: {str(e)}")
        traceback.print_exc()
        
        failed_parses += 1
        issues_found.append({
            'resume': resume_name,
            'issue': 'Exception during parsing',
            'details': str(e)
        })
        
        all_results.append({
            'name': resume_name,
            'success': False,
            'error': str(e)
        })

# Summary Report
print("\n" + "=" * 100)
print("📊 COMPREHENSIVE TEST SUMMARY")
print("=" * 100)

print(f"\n📈 Overall Statistics:")
print(f"   Total Resumes Tested: {total_resumes}")
print(f"   Successful Parses: {successful_parses} ({successful_parses/total_resumes*100:.1f}%)")
print(f"   Failed Parses: {failed_parses} ({failed_parses/total_resumes*100:.1f}%)")
print(f"   Total Issues Found: {len(issues_found)}")

# Section detection statistics
if all_results:
    successful_results = [r for r in all_results if r.get('success')]
    
    if successful_results:
        print(f"\n📂 Section Detection Stats (from {len(successful_results)} successful parses):")
        
        # Count section detection
        experience_detected = sum(1 for r in successful_results if r['section_status'].get('experience') in ['ok', 'empty'])
        education_detected = sum(1 for r in successful_results if r['section_status'].get('education') in ['ok', 'empty'])
        skills_detected = sum(1 for r in successful_results if r['section_status'].get('skills') in ['ok', 'empty'])
        
        print(f"   Experience: {experience_detected}/{len(successful_results)} ({experience_detected/len(successful_results)*100:.1f}%)")
        print(f"   Education: {education_detected}/{len(successful_results)} ({education_detected/len(successful_results)*100:.1f}%)")
        print(f"   Skills: {skills_detected}/{len(successful_results)} ({skills_detected/len(successful_results)*100:.1f}%)")
        
        # Name and email detection
        names_detected = sum(1 for r in successful_results if r['has_name'])
        emails_detected = sum(1 for r in successful_results if r['has_email'])
        
        print(f"\n👤 Information Extraction:")
        print(f"   Names Detected: {names_detected}/{len(successful_results)} ({names_detected/len(successful_results)*100:.1f}%)")
        print(f"   Emails Detected: {emails_detected}/{len(successful_results)} ({emails_detected/len(successful_results)*100:.1f}%)")
        
        # Average quality
        avg_quality = sum(r['quality_score'] for r in successful_results) / len(successful_results)
        print(f"\n⭐ Average Quality Score: {avg_quality:.1f}/100")

# Issues by type
if issues_found:
    print(f"\n⚠️  ISSUES BREAKDOWN ({len(issues_found)} total):")
    
    issue_types = {}
    for issue in issues_found:
        issue_type = issue['issue']
        if issue_type not in issue_types:
            issue_types[issue_type] = []
        issue_types[issue_type].append(issue['resume'])
    
    for issue_type, resumes in sorted(issue_types.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"\n   {issue_type} ({len(resumes)} occurrences):")
        for resume in resumes[:5]:  # Show first 5
            print(f"      • {resume}")
        if len(resumes) > 5:
            print(f"      ... and {len(resumes) - 5} more")

# Resumes with most issues
print(f"\n🔴 Resumes with Most Issues:")
resume_issue_counts = {}
for issue in issues_found:
    resume = issue['resume']
    resume_issue_counts[resume] = resume_issue_counts.get(resume, 0) + 1

top_problem_resumes = sorted(resume_issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]
for resume, count in top_problem_resumes:
    print(f"   • {resume}: {count} issues")

# Best performing resumes
print(f"\n🟢 Best Performing Resumes (Quality Score):")
successful_results = [r for r in all_results if r.get('success')]
top_quality = sorted(successful_results, key=lambda x: x['quality_score'], reverse=True)[:5]
for result in top_quality:
    print(f"   • {result['name']}: {result['quality_score']:.1f}/100")

print("\n" + "=" * 100)
print("✅ TESTING COMPLETE!")
print("=" * 100)

# Final assessment
if failed_parses == 0 and len(issues_found) < total_resumes * 0.2:  # Less than 20% issue rate
    print("\n🎉 EXCELLENT! System performs well on real-world resumes!")
elif failed_parses == 0 and len(issues_found) < total_resumes * 0.5:  # Less than 50% issue rate
    print("\n👍 GOOD! System works but some improvements needed for edge cases.")
else:
    print("\n⚠️  ATTENTION NEEDED! Several issues found that should be addressed.")

print("\n💡 Next Steps:")
if failed_parses > 0:
    print(f"   1. Fix {failed_parses} parsing failures")
if any('section empty' in i['issue'] for i in issues_found):
    print(f"   2. Investigate empty section content issues")
if any('not detected' in i['issue'].lower() for i in issues_found):
    print(f"   3. Improve name/email/section detection algorithms")

print("\n" + "=" * 100)
