"""
Interview Question Generator
Generates behavioral and technical interview questions from resume + job description.
Produces question items with: question text, intent, difficulty (1-5), follow-ups, expected focus areas.
"""

import re
from typing import Dict, List, Any


class InterviewQuestionGenerator:
    """Generate interview questions from candidate resume and job posting."""

    TECH_SKILLS = ['python','java','javascript','react','angular','aws','docker','kubernetes','sql','postgresql','mongodb','tensorflow','pytorch','nlp','spark','hadoop']
    BEHAVIORAL_PROMPTS = [
        'Tell me about a time when',
        'Describe a situation where',
        'Give an example of when you',
        'How did you handle',
        'What was a challenge you faced with'
    ]

    def __init__(self):
        pass

    def generate(self, resume: Dict[str, Any], job: Dict[str, Any], max_questions: int = 15) -> Dict[str, Any]:
        """
        Return a dictionary with generated questions grouped by type.
        resume: parsed resume dict (fields used: skills, experience, projects, summary)
        job: parsed job dict or plain job_text (fields used: skills_requirements, responsibilities, job_title)
        """
        skills = self._extract_skills_from_resume(resume)
        job_skills = self._extract_skills_from_job(job)
        experiences = resume.get('experience', []) if isinstance(resume.get('experience', []), list) else []
        projects = resume.get('projects', []) if isinstance(resume.get('projects', []), list) else []

        questions = {
            'behavioral': [],
            'technical': [],
            'projects': [],
            'role_fit': []
        }

        # Behavioral: use top experiences and generate STAR-style prompts
        top_exps = experiences[:3]
        for exp in top_exps:
            title = exp.get('title') or exp.get('role') or exp.get('position') or 'your role'
            org = exp.get('company') or exp.get('organization') or ''
            q_text = f"{self._pick_behavioral_prefix()} a time you worked as {title} at {org}: what was the situation, what actions did you take, and what was the outcome?"
            questions['behavioral'].append(self._make_question(q_text, intent='leadership/problem_solving', difficulty=2))

        # Behavioral from timeline/gap indicators
        timeline = resume.get('timeline_analysis', {})
        if timeline and timeline.get('job_hopping_score') is not None:
            score = timeline.get('job_hopping_score')
            if score > 0.6:
                q = "I noticed you've changed roles frequently in a short time frame — can you walk me through the reasons and what you learned from each move?"
                questions['behavioral'].append(self._make_question(q, intent='stability', difficulty=3))

        # Technical: From intersection of resume skills and job_skills first, then resume-only, then job-only
        combined_priority = []
        for s in job_skills:
            if s in skills:
                combined_priority.append(s)
        for s in skills:
            if s not in combined_priority:
                combined_priority.append(s)
        for s in job_skills:
            if s not in combined_priority:
                combined_priority.append(s)

        # Make up to max_questions technical questions
        tech_count = 0
        for skill in combined_priority:
            if tech_count >= max_questions:
                break
            q = self._technical_question_for_skill(skill, resume, job)
            questions['technical'].append(q)
            tech_count += 1

        # Project-based: ask detailed questions about projects in resume
        for proj in projects[:5]:
            title = proj.get('title') or proj.get('name') or 'a project you worked on'
            desc = proj.get('description') or proj.get('summary') or ''
            q = f"Describe the architecture and your specific contributions to {title}. What tradeoffs did you consider and why?"
            questions['projects'].append(self._make_question(q, intent='technical_depth', difficulty=3))

        # Role-fit: based on responsibilities
        responsibilities = (job.get('responsibilities') or [])
        if isinstance(responsibilities, list):
            for r in responsibilities[:5]:
                q = f"This role requires: {r[:100]}... Can you share an example from your background that demonstrates you can do this?"
                questions['role_fit'].append(self._make_question(q, intent='role_fit', difficulty=2))

        # Fillers: if not many questions generated, add generic questions
        if sum(len(v) for v in questions.values()) < 6:
            questions['behavioral'].append(self._make_question("Tell me about a challenging technical problem you solved recently and how you approached it.", intent='problem_solving', difficulty=2))
            questions['technical'].append(self._make_question("Explain the pros and cons of monolithic vs microservices architectures.", intent='system_design', difficulty=3))

        # Rank and trim
        for k in list(questions.keys()):
            questions[k] = questions[k][:max_questions]

        return {
            'job_title': job.get('job_title') if isinstance(job, dict) else None,
            'counts': {k: len(v) for k, v in questions.items()},
            'questions': questions
        }

    def _extract_skills_from_resume(self, resume: Dict[str, Any]) -> List[str]:
        skills = []
        sdata = resume.get('skills')
        if isinstance(sdata, dict):
            skills = [s.lower() for s in sdata.get('all_skills', [])]
        elif isinstance(sdata, list):
            skills = [s.lower() for s in sdata]
        # normalize
        skills = [re.sub(r'[^a-z0-9+#+\.\- ]', '', s).strip() for s in skills]
        return skills

    def _extract_skills_from_job(self, job: Dict[str, Any]) -> List[str]:
        skills = []
        if isinstance(job, dict):
            sk = job.get('skills_requirements')
            if isinstance(sk, dict):
                skills = [s.lower() for s in sk.get('required_skills', [])]
                skills += [s.lower() for s in sk.get('nice_to_have_skills', [])]
            elif isinstance(sk, list):
                skills = [s.lower() for s in sk]
            else:
                # Try parsing job text
                text = job.get('text') or ''
                skills = [s for s in self.TECH_SKILLS if s in text.lower()]
        elif isinstance(job, str):
            text = job.lower()
            skills = [s for s in self.TECH_SKILLS if s in text]
        skills = list(dict.fromkeys(skills))
        return skills

    def _pick_behavioral_prefix(self) -> str:
        import random
        return random.choice(self.BEHAVIORAL_PROMPTS)

    def _technical_question_for_skill(self, skill: str, resume: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        skill_clean = skill.lower()
        difficulty = 2
        intent = 'knowledge'
        followups = []

        # Heuristics to set difficulty
        if skill_clean in ['kubernetes','spark','hadoop','tensorflow','pytorch']:
            difficulty = 4
            intent = 'platform_expertise'
        elif skill_clean in ['aws','docker','microservices']:
            difficulty = 3
            intent = 'infrastructure'
        elif skill_clean in ['react','angular','javascript']:
            difficulty = 3
            intent = 'frontend'
        elif skill_clean in ['python','java','sql']:
            difficulty = 2
            intent = 'implementation'

        # Build question text
        q_text = f"Explain your experience with {skill_clean}. Describe a concrete example where you used it, the challenges you faced and the results."

        # Add follow-up prompts
        followups.append(f"How did you measure success for your work with {skill_clean}?")
        followups.append(f"What trade-offs did you consider when choosing {skill_clean} for that solution?")

        return self._make_question(q_text, intent=intent, difficulty=difficulty, follow_ups=followups)

    def _make_question(self, text: str, intent: str = 'general', difficulty: int = 2, follow_ups: List[str] = None) -> Dict[str, Any]:
        return {
            'question': text,
            'intent': intent,
            'difficulty': int(max(1, min(5, difficulty))),
            'follow_ups': follow_ups or []
        }


# ===================== SELF TEST =====================
if __name__ == '__main__':
    # Minimal sample resume and job
    sample_resume = {
        'skills': {'all_skills': ['Python', 'Django', 'AWS', 'Docker', 'Kubernetes']},
        'experience': [
            {'title':'Senior Software Engineer','company':'Acme Inc','description':'Led a team building microservices on AWS using Docker and Kubernetes. Improved latency by 30%.'},
            {'title':'Software Engineer','company':'Beta LLC','description':'Built APIs in Python and Django backed by PostgreSQL.'}
        ],
        'projects': [
            {'title':'Realtime Analytics','description':'Built a streaming analytics pipeline using Spark and Kafka.'}
        ],
        'timeline_analysis': {'job_hopping_score':0.2}
    }

    sample_job = {
        'job_title':'Senior Backend Engineer',
        'skills_requirements': {
            'required_skills': ['Python', 'AWS', 'Docker', 'Microservices'],
            'nice_to_have_skills': ['Kubernetes', 'Spark']
        },
        'responsibilities': [
            'Design and implement scalable backend systems',
            'Lead technical decisions and architecture',
            'Mentor junior developers'
        ]
    }

    gen = InterviewQuestionGenerator()
    out = gen.generate(sample_resume, sample_job, max_questions=10)

    print('Interview Questions Generated:')
    print('Counts:', out['counts'])
    print('\nSample Technical Questions:')
    for q in out['questions']['technical'][:5]:
        print('-', q['question'])
        for f in q['follow_ups']:
            print('   →', f)
    
    print('\nSample Behavioral Questions:')
    for q in out['questions']['behavioral']:
        print('-', q['question'])

    print('\nRole-fit Questions:')
    for q in out['questions']['role_fit']:
        print('-', q['question'])

    print('\nProjects Questions:')
    for q in out['questions']['projects']:
        print('-', q['question'])
