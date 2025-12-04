"""
Automated Resume Formatting Suggestions

Analyzes a parsed resume and returns:
- concrete suggestions (section order, missing sections, length fixes)
- bulletification suggestions for experience descriptions
- a cleaned resume text template (simple plain-text output) that can be applied

This is a rule-based, safe module that does not change PDF formatting; it outputs suggested plain-text transformations.
"""

import re
from typing import Dict, List

DEFAULT_SECTION_ORDER = [
    'contact_info', 'summary', 'skills', 'experience', 'projects', 'education', 'certifications', 'additional'
]

class FormattingSuggester:
    def __init__(self):
        pass

    def suggest(self, resume: Dict) -> Dict:
        """Return suggestions and a cleaned template.
        resume: parsed resume dict (may have keys like 'contact_info','summary','skills','experience','projects','education')
        """
        suggestions = []
        cleaned = {
            'header': '',
            'sections': {}
        }

        # Header / contact
        contact = resume.get('contact_info') or {}
        header_lines = []
        if isinstance(contact, dict):
            name = contact.get('name') or ''
            email = contact.get('email') or ''
            phone = contact.get('phone') or ''
            location = contact.get('location') or ''
            if name:
                header_lines.append(name.strip())
            if email:
                header_lines.append(email.strip())
            if phone:
                header_lines.append(phone.strip())
            if location:
                header_lines.append(location.strip())
        else:
            # if contact is just text
            header_lines.append(str(contact))

        cleaned['header'] = ' | '.join([l for l in header_lines if l])
        if not cleaned['header']:
            suggestions.append('Add contact header: name, email, phone, location')

        # Section ordering
        present_sections = [s for s in DEFAULT_SECTION_ORDER if resume.get(s)]
        missing_sections = [s for s in DEFAULT_SECTION_ORDER if s not in present_sections]
        if 'experience' not in present_sections:
            suggestions.append('Add an Experience section (work history) with company, title, dates, and 3-5 bullet achievements per role')
        else:
            # check experience formatting
            exps = resume.get('experience') or []
            if isinstance(exps, list):
                for i, e in enumerate(exps[:5]):
                    desc = e.get('description') or e.get('responsibilities') or ''
                    if desc and not self._has_bullets(desc):
                        suggestions.append(f"Role '{e.get('title','(no title)')}' at '{e.get('company','')}' uses paragraphs — consider converting key achievements into 3-5 concise bullets.")

        # Skills section
        skills = resume.get('skills')
        skill_count = 0
        if skills:
            if isinstance(skills, dict):
                skill_list = skills.get('all_skills', [])
            else:
                skill_list = skills
            skill_count = len(skill_list)
            if skill_count < 5:
                suggestions.append('Skills section is short — target 8-15 concise skill phrases (e.g., Python, Django, AWS).')
            elif skill_count > 50:
                suggestions.append('Skills list is long — group into categories (Languages, Frameworks, DevOps, Data) and prioritize the most relevant 15-20.')

            # Build cleaned skills
            cleaned['sections']['skills'] = ', '.join(skill_list[:50])
        else:
            suggestions.append('Add a dedicated Skills section (comma-separated list of core skills).')

        # Summary
        summary = resume.get('summary') or resume.get('objective') or ''
        if summary:
            # check length
            words = len(summary.split())
            if words > 80:
                suggestions.append('Summary is lengthy — shorten to 40-60 words emphasizing core strengths and target role.')
            cleaned['sections']['summary'] = self._one_line(summary)
        else:
            suggestions.append('Add a concise 2-3 sentence professional summary at the top.')

        # Projects
        projects = resume.get('projects') or []
        proj_suggestions = []
        cleaned_projects = []
        if projects and isinstance(projects, list):
            for p in projects[:5]:
                title = p.get('title') or p.get('name') or 'Project'
                desc = p.get('description') or p.get('summary') or ''
                if desc and len(desc.split()) > 60:
                    proj_suggestions.append(f"Project '{title}' description is long — shorten to 1-3 bullets focusing on your role and impact.")
                cleaned_projects.append(f"{title}: {self._one_line(desc)}")
            cleaned['sections']['projects'] = '\n'.join(cleaned_projects)
        
        if proj_suggestions:
            suggestions += proj_suggestions

        # Education
        education = resume.get('education') or []
        if not education:
            suggestions.append('Add Education section (degree, institution, graduation year). If no degree, list relevant certifications or training.')
        else:
            # check for dates and order
            if isinstance(education, list):
                first = education[0]
                if not first.get('degree'):
                    suggestions.append('Education entries should include degree or certification title.')
                cleaned_edu = []
                for e in education[:3]:
                    deg = e.get('degree') or ''
                    inst = e.get('institution') or e.get('school') or ''
                    year = e.get('year') or e.get('graduation') or ''
                    cleaned_edu.append(' '.join([str(x) for x in [deg, inst, year] if x]))
                cleaned['sections']['education'] = '\n'.join(cleaned_edu)

        # Length guidance
        text = resume.get('text') or ''
        wc = len(text.split()) if text else 0
        if wc == 0:
            suggestions.append('Resume text appears empty — ensure parsed text is available or upload a different format.')
        else:
            if wc < 300:
                suggestions.append(f'Resume is short ({wc} words) — aim for 400-800 words for most mid/senior roles.')
            elif wc > 1200:
                suggestions.append(f'Resume is long ({wc} words) — reduce to 800 words by focusing on most recent 10-15 years and top achievements.')

        # ATS friendliness
        headers_in_text = sum(1 for h in ['experience','education','skills','summary'] if h in (text or '').lower())
        if headers_in_text < 2:
            suggestions.append('Add clear section headers (Experience, Education, Skills, Summary) to improve ATS parsing.')

        # Generate cleaned template text using cleaned dict and default order
        template_lines = []
        if cleaned['header']:
            template_lines.append(cleaned['header'])
            template_lines.append('\n')

        for sec in DEFAULT_SECTION_ORDER:
            sec_key = sec
            if sec_key in cleaned['sections']:
                template_lines.append(sec_key.replace('_',' ').title())
                template_lines.append(cleaned['sections'][sec_key])
                template_lines.append('\n')
            elif resume.get(sec):
                # Use existing content, but normalize
                if sec == 'experience':
                    exps = resume.get('experience', [])
                    template_lines.append('Experience')
                    for e in exps[:8]:
                        title = e.get('title') or e.get('role') or ''
                        comp = e.get('company') or ''
                        dates = e.get('dates') or e.get('date') or ''
                        desc = e.get('description') or ''
                        bullets = self._to_bullets(desc)
                        template_lines.append(f"{title} — {comp} | {dates}")
                        for b in bullets[:5]:
                            template_lines.append(f"- {b}")
                        template_lines.append('')
                    template_lines.append('\n')
                else:
                    val = resume.get(sec)
                    template_lines.append(sec.replace('_',' ').title())
                    template_lines.append(self._one_line(str(val)[:400]))
                    template_lines.append('\n')

        cleaned_text = '\n'.join(template_lines).strip()

        return {
            'suggestions': suggestions,
            'cleaned_resume_text': cleaned_text,
            'missing_sections': missing_sections,
            'skill_count': skill_count,
            'word_count': wc
        }

    def _has_bullets(self, text: str) -> bool:
        return bool(re.search(r'(^|\n)\s*[-•*]', text))

    def _to_bullets(self, text: str) -> List[str]:
        # If already bullets, return lines
        if self._has_bullets(text):
            lines = [l.strip('-•* \t') for l in text.split('\n') if l.strip()]
            return [l for l in lines if l]
        # else split into sentences and return as bullets
        sentences = re.split(r'(?<=[.!?])\s+', text)
        bullets = [s.strip() for s in sentences if len(s.strip()) > 20]
        return bullets

    def _one_line(self, text: str) -> str:
        # collapse whitespace and return single line of reasonable length
        line = ' '.join(text.split())
        if len(line) > 200:
            # truncate politely
            return line[:197].rsplit(' ',1)[0] + '...'
        return line


# ================= SELF-TEST =================
if __name__ == '__main__':
    sample = {
        'contact_info': {'name':'Jane Doe','email':'jane@example.com','phone':'(555) 555-5555','location':'London, UK'},
        'summary': 'Experienced software engineer with a strong background in backend systems, performance optimization and cloud infrastructure. Passionate about building scalable services.',
        'skills': {'all_skills':['Python','Django','AWS','Docker','Kubernetes','PostgreSQL']},
        'experience': [
            {'title':'Senior Software Engineer','company':'Acme','dates':'2019-2024','description':'I was responsible for building services. I worked on multiple projects where I implemented features and fixed bugs, coordinated with team members and ensured delivery of projects on time. Improved latency by 30% on key endpoints.'},
            {'title':'Software Engineer','company':'Beta','dates':'2016-2019','description':'Worked on web applications using Django. Participated in code reviews and improved testing coverage.'}
        ],
        'projects':[{'title':'Realtime Analytics','description':'Built a streaming pipeline using Spark and Kafka to process events.'}],
        'education':[{'degree':'BSc Computer Science','institution':'University X','year':'2016'}],
        'text': 'Sample resume text with Experience, Education and Skills headers.'
    }

    sugg = FormattingSuggester()
    out = sugg.suggest(sample)
    print('Suggestions:')
    for s in out['suggestions']:
        print('-', s)
    print('\nWord count:', out['word_count'])
    print('\nCleaned Resume Preview:\n')
    print(out['cleaned_resume_text'][:1200])
