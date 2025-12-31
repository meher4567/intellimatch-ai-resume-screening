"""
Enhanced Resume Quality Scorer
Provides high-level, actionable quality assessment for uploaded resumes

This scorer focuses on what matters most:
1. Is the resume complete and professional?
2. What's missing that would hurt job applications?
3. What are the strengths to highlight?
4. What needs immediate improvement?

DYNAMIC SCORING:
- Base score (static criteria)
- Bonus points for exceptional features
- Penalty for red flags
- Job-specific relevance (when job description provided)
- Industry-specific adjustments

Returns a simple A-F grade with clear feedback.
"""

import re
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class ResumeGrade:
    """Resume quality grade with feedback"""
    score: float  # 0-100
    grade: str  # A, B, C, D, F
    tier: str  # "Excellent", "Good", "Average", "Needs Work", "Poor"
    summary: str  # One-line summary
    strengths: List[str]  # What's good
    improvements: List[str]  # What to fix (prioritized)
    missing: List[str]  # Critical missing elements
    ats_score: float  # ATS compatibility 0-100
    # Dynamic scoring breakdown
    breakdown: Dict[str, float] = field(default_factory=dict)
    bonuses: List[str] = field(default_factory=list)
    penalties: List[str] = field(default_factory=list)
    job_relevance_score: Optional[float] = None  # 0-100 if job provided
    
    def to_dict(self) -> Dict:
        return {
            "score": round(self.score, 1),
            "grade": self.grade,
            "tier": self.tier,
            "summary": self.summary,
            "strengths": self.strengths,
            "improvements": self.improvements,
            "missing": self.missing,
            "ats_score": round(self.ats_score, 1),
            "breakdown": {k: round(v, 1) for k, v in self.breakdown.items()},
            "bonuses": self.bonuses,
            "penalties": self.penalties,
            "job_relevance_score": round(self.job_relevance_score, 1) if self.job_relevance_score else None
        }


class EnhancedQualityScorer:
    """
    Dynamic Resume Quality Scorer with context-aware scoring
    
    BASE SCORING (80 points):
    - Contact Info (8): Email, phone, LinkedIn
    - Professional Summary (12): Clear summary/objective
    - Experience Section (20): Jobs with dates, achievements
    - Skills Section (12): Technical and soft skills
    - Education (8): Degrees, certifications
    - Formatting (8): Clean, readable, ATS-friendly
    - Quantification (8): Numbers, metrics, achievements
    - Length (4): Appropriate length (1-2 pages)
    
    DYNAMIC BONUSES (up to +25):
    - Career progression (+5)
    - Relevant certifications (+5)
    - Project diversity (+4)
    - Industry keywords (+3)
    - Recent skill updates (+3)
    - International experience (+2)
    - Leadership indicators (+3)
    
    PENALTIES (up to -15):
    - Employment gaps (-5)
    - Outdated skills (-3)
    - Generic descriptions (-3)
    - Typos/errors (-4)
    """
    
    def __init__(self):
        # Action verbs that indicate strong experience descriptions
        self.action_verbs = {
            "led", "managed", "developed", "created", "implemented", "designed",
            "built", "achieved", "increased", "decreased", "reduced", "improved",
            "launched", "delivered", "analyzed", "coordinated", "established",
            "generated", "optimized", "streamlined", "spearheaded", "mentored",
            "collaborated", "negotiated", "resolved", "executed", "transformed",
            "architected", "automated", "scaled", "pioneered", "innovated"
        }
        
        # Keywords that indicate quantification
        self.quant_patterns = [
            r'\d+%',  # Percentages
            r'\$[\d,]+[KMB]?',  # Dollar amounts
            r'\d+\+?\s*(years?|months?)',  # Experience duration
            r'\d+\s*(team|people|members|employees|engineers)',  # Team size
            r'\d+\s*(projects?|clients?|customers?|users?)',  # Scale
            r'increased\s*\w*\s*by\s*\d+',  # Impact
            r'reduced\s*\w*\s*by\s*\d+',  # Impact
            r'saved\s*\w*\s*\$?\d+',  # Cost savings
            r'\d+x\s*(faster|improvement|growth)',  # Multiplier improvements
            r'top\s*\d+%',  # Rankings
        ]
        
        # High-value certifications by domain
        self.valuable_certifications = {
            "cloud": ["aws", "azure", "gcp", "google cloud", "certified solutions architect", 
                      "cloud practitioner", "devops engineer"],
            "security": ["cissp", "ceh", "security+", "oscp", "comptia security"],
            "data": ["google data engineer", "aws data", "databricks", "snowflake"],
            "pm": ["pmp", "scrum master", "csm", "safe", "agile certified"],
            "ml": ["tensorflow", "pytorch certified", "aws ml", "google ml"],
        }
        
        # Leadership indicators
        self.leadership_keywords = {
            "led", "managed", "directed", "supervised", "mentored", "coached",
            "team lead", "tech lead", "senior", "principal", "architect",
            "head of", "director", "vp", "chief", "founder", "co-founder"
        }
        
        # Industry-specific keyword sets
        self.industry_keywords = {
            "tech": {"agile", "scrum", "ci/cd", "devops", "microservices", "cloud", 
                     "kubernetes", "docker", "api", "rest", "graphql"},
            "finance": {"fintech", "trading", "risk", "compliance", "regulations",
                        "portfolio", "investment", "banking", "securities"},
            "healthcare": {"hipaa", "ehr", "clinical", "medical", "patient", 
                          "healthcare", "pharma", "fda"},
            "data": {"machine learning", "ai", "data science", "analytics",
                    "big data", "etl", "data pipeline", "visualization"},
        }
        
        # Skills that may be outdated
        self.outdated_skills = {
            "flash", "actionscript", "coldfusion", "foxpro", "visual basic 6",
            "cobol", "fortran", "delphi", "silverlight", "windows xp",
            "ie6", "ie7", "jquery ui", "backbone.js"
        }
        
        # Modern/in-demand skills (bonus)
        self.modern_skills = {
            "kubernetes", "docker", "terraform", "aws", "azure", "gcp",
            "react", "vue", "angular", "typescript", "golang", "rust",
            "machine learning", "deep learning", "pytorch", "tensorflow",
            "graphql", "microservices", "kafka", "elasticsearch"
        }
    
    def score_resume(self, parsed_data: Dict[str, Any], 
                     job_description: Optional[str] = None,
                     target_role: Optional[str] = None) -> ResumeGrade:
        """
        Score a parsed resume with dynamic adjustments
        
        Args:
            parsed_data: Output from ResumeParser
            job_description: Optional job description for relevance scoring
            target_role: Optional target role/title for context
            
        Returns:
            ResumeGrade with score, breakdown, and actionable feedback
        """
        scores = {}
        strengths = []
        improvements = []
        missing = []
        bonuses = []
        penalties = []
        
        # Get text and sections
        text = parsed_data.get("text", "")
        text_lower = text.lower()
        sections = parsed_data.get("sections", {})
        contact = parsed_data.get("contact_info", {})
        experience = parsed_data.get("experience", [])
        skills = parsed_data.get("skills", {})
        
        # ============ BASE SCORING (80 points) ============
        
        # 1. Contact Info (8 points)
        scores["contact"] = self._score_contact(contact, strengths, improvements, missing)
        
        # 2. Professional Summary (12 points)
        scores["summary"] = self._score_summary(sections, text, strengths, improvements, missing)
        
        # 3. Experience (20 points)
        scores["experience"] = self._score_experience(experience, sections, text, strengths, improvements, missing)
        
        # 4. Skills (12 points)
        scores["skills"] = self._score_skills(skills, sections, strengths, improvements, missing)
        
        # 5. Education (8 points)
        scores["education"] = self._score_education(sections, parsed_data, strengths, improvements, missing)
        
        # 6. Formatting (8 points)
        scores["formatting"] = self._score_formatting(sections, text, parsed_data, strengths, improvements)
        
        # 7. Quantification (8 points)
        scores["quantification"] = self._score_quantification(text, experience, strengths, improvements)
        
        # 8. Length (4 points)
        scores["length"] = self._score_length(text, parsed_data, improvements)
        
        base_score = sum(scores.values())
        
        # ============ DYNAMIC BONUSES (up to +25) ============
        
        bonus_score = 0.0
        
        # Career Progression (+5)
        progression_bonus = self._check_career_progression(experience)
        if progression_bonus > 0:
            bonus_score += progression_bonus
            bonuses.append(f"Career progression: +{progression_bonus}")
            strengths.append("Clear career growth trajectory")
        
        # Certifications (+5)
        cert_bonus = self._check_certifications(text_lower, sections)
        if cert_bonus > 0:
            bonus_score += cert_bonus
            bonuses.append(f"Valuable certifications: +{cert_bonus}")
            strengths.append("Relevant professional certifications")
        
        # Project Diversity (+4)
        project_bonus = self._check_project_diversity(parsed_data, text_lower)
        if project_bonus > 0:
            bonus_score += project_bonus
            bonuses.append(f"Project diversity: +{project_bonus}")
        
        # Modern Skills (+3)
        modern_bonus = self._check_modern_skills(skills, text_lower)
        if modern_bonus > 0:
            bonus_score += modern_bonus
            bonuses.append(f"Modern tech stack: +{modern_bonus}")
            strengths.append("Up-to-date with modern technologies")
        
        # Leadership Indicators (+3)
        leadership_bonus = self._check_leadership(text_lower, experience)
        if leadership_bonus > 0:
            bonus_score += leadership_bonus
            bonuses.append(f"Leadership experience: +{leadership_bonus}")
            strengths.append("Demonstrated leadership abilities")
        
        # Industry Keywords (+3)
        industry_bonus = self._check_industry_keywords(text_lower)
        if industry_bonus > 0:
            bonus_score += industry_bonus
            bonuses.append(f"Industry expertise: +{industry_bonus}")
        
        # International/Remote Experience (+2)
        intl_bonus = self._check_international(text_lower)
        if intl_bonus > 0:
            bonus_score += intl_bonus
            bonuses.append(f"Global experience: +{intl_bonus}")
        
        # ============ PENALTIES (up to -15) ============
        
        penalty_score = 0.0
        
        # Employment Gaps (-5)
        gap_penalty = self._check_employment_gaps(experience)
        if gap_penalty > 0:
            penalty_score += gap_penalty
            penalties.append(f"Employment gaps: -{gap_penalty}")
            improvements.append("Address or explain employment gaps")
        
        # Outdated Skills (-3)
        outdated_penalty = self._check_outdated_skills(skills, text_lower)
        if outdated_penalty > 0:
            penalty_score += outdated_penalty
            penalties.append(f"Outdated technologies: -{outdated_penalty}")
            improvements.append("Update skills section with current technologies")
        
        # Generic Descriptions (-3)
        generic_penalty = self._check_generic_content(text_lower)
        if generic_penalty > 0:
            penalty_score += generic_penalty
            penalties.append(f"Generic descriptions: -{generic_penalty}")
            improvements.append("Replace generic phrases with specific achievements")
        
        # Missing Impact Statements (-4)
        impact_penalty = self._check_impact_statements(experience, text)
        if impact_penalty > 0:
            penalty_score += impact_penalty
            penalties.append(f"Missing impact: -{impact_penalty}")
        
        # ============ CALCULATE FINAL SCORE ============
        
        total_score = min(100, max(0, base_score + bonus_score - penalty_score))
        
        # Calculate ATS score
        ats_score = self._calculate_ats_score(parsed_data, scores)
        
        # Job relevance (if job description provided)
        job_relevance = None
        if job_description:
            job_relevance = self._calculate_job_relevance(parsed_data, job_description, target_role)
            if job_relevance >= 70:
                strengths.append(f"Strong match for target role ({job_relevance:.0f}%)")
            elif job_relevance < 40:
                improvements.append("Resume may need tailoring for this specific role")
        
        # Determine grade
        grade, tier = self._get_grade(total_score)
        
        # Generate summary
        summary = self._generate_summary(total_score, grade, missing, len(experience), bonuses, penalties)
        
        # Prioritize improvements
        improvements = self._prioritize_improvements(improvements, scores)
        
        return ResumeGrade(
            score=total_score,
            grade=grade,
            tier=tier,
            summary=summary,
            strengths=strengths[:6],  # Top 6 strengths
            improvements=improvements[:6],  # Top 6 improvements
            missing=missing,
            ats_score=ats_score,
            breakdown=scores,
            bonuses=bonuses,
            penalties=penalties,
            job_relevance_score=job_relevance
        )
    
    def _score_contact(self, contact: Dict, strengths: List, improvements: List, missing: List) -> float:
        """Score contact information (0-8)"""
        score = 0.0
        
        # Email (required - 3 points)
        emails = contact.get("emails", [])
        if emails:
            score += 3.0
            if any("gmail" in e or "outlook" in e or "yahoo" in e for e in emails):
                pass  # Personal email is fine
            else:
                strengths.append("Professional email domain")
        else:
            missing.append("Email address")
        
        # Phone (important - 2 points)
        phones = contact.get("phones", [])
        if phones:
            score += 2.0
        else:
            improvements.append("Add phone number for better contact options")
        
        # LinkedIn (nice to have - 2 points)
        if contact.get("linkedin"):
            score += 2.0
            strengths.append("LinkedIn profile included")
        else:
            improvements.append("Add LinkedIn profile URL")
        
        # GitHub/Portfolio (bonus - 1 point)
        if contact.get("github") or contact.get("website"):
            score += 1.0
            strengths.append("Portfolio/GitHub included")
        
        return min(8.0, score)
    
    def _score_summary(self, sections: Dict, text: str, strengths: List, improvements: List, missing: List) -> float:
        """Score professional summary (0-12)"""
        score = 0.0
        
        # Check for summary section
        summary_section = sections.get("summary", {}) or sections.get("objective", {}) or sections.get("profile", {})
        
        if summary_section:
            content = summary_section.get("content", "")
            word_count = len(content.split())
            
            if word_count >= 20:
                score += 8.0
                
                # Check quality of summary
                if word_count <= 80:
                    score += 2.0  # Concise is good
                    strengths.append("Clear, concise professional summary")
                else:
                    improvements.append("Shorten summary to 2-3 sentences")
                    score += 1.0
                
                # Check for keywords
                keywords = ["experience", "skills", "expertise", "professional", "years"]
                if any(kw in content.lower() for kw in keywords):
                    score += 2.0
            else:
                score += 4.0
                improvements.append("Expand professional summary with key qualifications")
        else:
            # Check first few lines for implicit summary
            first_lines = text[:500].lower()
            if any(word in first_lines for word in ["objective", "summary", "seeking", "professional"]):
                score += 4.0
                improvements.append("Add a clearly labeled 'Professional Summary' section")
            else:
                missing.append("Professional Summary/Objective")
                improvements.append("Add a 2-3 sentence professional summary at the top")
        
        return min(12.0, score)
    
    def _score_experience(self, experience: List, sections: Dict, text: str, 
                         strengths: List, improvements: List, missing: List) -> float:
        """Score experience section (0-20)"""
        score = 0.0
        
        exp_section = sections.get("experience", {}) or sections.get("work", {})
        
        if not experience and not exp_section:
            missing.append("Work Experience section")
            return 0.0
        
        # Has experience section
        score += 4.0
        
        # Number of positions
        num_positions = len(experience) if experience else 0
        
        if num_positions >= 3:
            score += 5.0
            strengths.append(f"{num_positions} work experiences documented")
        elif num_positions >= 1:
            score += 3.0
        
        # Check experience quality
        if experience:
            has_dates = sum(1 for exp in experience if exp.get("start_date") or exp.get("end_date"))
            has_company = sum(1 for exp in experience if exp.get("company"))
            has_title = sum(1 for exp in experience if exp.get("title"))
            has_achievements = sum(1 for exp in experience if exp.get("achievements"))
            
            # Dates (5 points)
            if has_dates >= num_positions * 0.8:
                score += 5.0
                strengths.append("Clear employment dates")
            elif has_dates > 0:
                score += 2.0
                improvements.append("Add dates to all work experiences")
            else:
                improvements.append("Add start/end dates for each position")
            
            # Company names (3 points)
            if has_company >= num_positions * 0.8:
                score += 3.0
            else:
                improvements.append("Include company names for all positions")
            
            # Job titles (3 points)
            if has_title >= num_positions * 0.8:
                score += 3.0
            else:
                improvements.append("Include job titles for all positions")
            
            # Achievements/bullets (4 points)
            if has_achievements >= num_positions * 0.5:
                score += 4.0
                strengths.append("Detailed achievement bullets")
            elif has_achievements > 0:
                score += 2.0
                improvements.append("Add more achievement bullets to experiences")
            else:
                improvements.append("Add bullet points describing achievements in each role")
        
        return min(20.0, score)
    
    def _score_skills(self, skills: Dict, sections: Dict, strengths: List, 
                     improvements: List, missing: List) -> float:
        """Score skills section (0-12)"""
        score = 0.0
        
        skills_section = sections.get("skills", {}) or sections.get("technical", {})
        all_skills = skills.get("all_skills", []) if isinstance(skills, dict) else []
        
        if not skills_section and not all_skills:
            missing.append("Skills section")
            return 0.0
        
        # Has skills section
        score += 4.0
        
        skill_count = len(all_skills)
        
        # Number of skills
        if skill_count >= 15:
            score += 5.0
            strengths.append(f"{skill_count} relevant skills listed")
        elif skill_count >= 8:
            score += 3.0
        elif skill_count >= 3:
            score += 1.0
            improvements.append("Add more skills (aim for 10-15)")
        
        # Skills categorization
        by_category = skills.get("by_category", {}) if isinstance(skills, dict) else {}
        if len(by_category) >= 2:
            score += 3.0
            strengths.append("Skills organized by category")
        elif skill_count > 10:
            improvements.append("Organize skills into categories (Technical, Soft, Tools)")
        
        # Technical vs soft skills balance
        technical = len(by_category.get("technical", []))
        soft = len(by_category.get("soft", []))
        
        if technical > 0 and soft > 0:
            score += 2.0
        elif technical > 0:
            improvements.append("Add some soft skills (communication, leadership, etc.)")
        
        return min(12.0, score)
    
    def _score_education(self, sections: Dict, parsed_data: Dict, strengths: List, 
                        improvements: List, missing: List) -> float:
        """Score education section (0-8)"""
        score = 0.0
        
        edu_section = sections.get("education", {}) or sections.get("academic", {})
        
        if not edu_section:
            missing.append("Education section")
            return 0.0
        
        content = edu_section.get("content", "")
        
        # Has education section
        score += 4.0
        
        # Check for degree
        degrees = ["bachelor", "master", "phd", "doctorate", "associate", "mba", 
                   "b.s.", "b.a.", "m.s.", "m.a.", "btech", "mtech", "engineering"]
        if any(deg in content.lower() for deg in degrees):
            score += 2.0
            strengths.append("Degree clearly stated")
        else:
            improvements.append("Clearly state your degree (e.g., Bachelor of Science)")
        
        # Check for GPA (if high)
        gpa_match = re.search(r'gpa[:\s]*(\d+\.?\d*)', content.lower())
        if gpa_match:
            gpa = float(gpa_match.group(1))
            if gpa >= 3.5 or (gpa >= 8.0 and gpa <= 10.0):  # US or Indian scale
                score += 2.0
                strengths.append(f"Strong GPA highlighted")
        
        return min(8.0, score)
    
    def _score_formatting(self, sections: Dict, text: str, parsed_data: Dict,
                         strengths: List, improvements: List) -> float:
        """Score formatting and structure (0-8)"""
        score = 4.0  # Baseline
        
        # Clear sections
        section_count = len(sections)
        if section_count >= 5:
            score += 2.0
            strengths.append("Well-organized with clear sections")
        elif section_count >= 3:
            score += 1.0
        else:
            improvements.append("Add clear section headers (Experience, Skills, Education)")
        
        # Not too many special characters (ATS friendly)
        special_chars = len(re.findall(r'[^\w\s.,;:()\-\'\"@/]', text))
        char_ratio = special_chars / max(len(text), 1)
        if char_ratio < 0.02:
            score += 2.0
        else:
            improvements.append("Reduce special characters for better ATS compatibility")
        
        # Check for bullet consistency
        bullets = len(re.findall(r'^[\s]*[•\-\*]', text, re.MULTILINE))
        if bullets >= 5:
            score += 1.0
        
        return min(8.0, score)
    
    def _score_quantification(self, text: str, experience: List, 
                             strengths: List, improvements: List) -> float:
        """Score use of numbers and metrics (0-8)"""
        score = 0.0
        
        # Count quantified statements
        quant_count = 0
        for pattern in self.quant_patterns:
            quant_count += len(re.findall(pattern, text, re.IGNORECASE))
        
        if quant_count >= 5:
            score += 5.0
            strengths.append("Strong use of metrics and numbers")
        elif quant_count >= 2:
            score += 3.0
        else:
            improvements.append("Add more numbers/metrics (e.g., 'increased sales by 20%')")
        
        # Action verbs
        text_lower = text.lower()
        action_count = sum(1 for verb in self.action_verbs if verb in text_lower)
        
        if action_count >= 5:
            score += 3.0
            strengths.append("Strong action verbs used")
        elif action_count >= 2:
            score += 1.5
        else:
            improvements.append("Use more action verbs (led, developed, achieved)")
        
        return min(8.0, score)
    
    def _score_length(self, text: str, parsed_data: Dict, improvements: List) -> float:
        """Score resume length (0-4)"""
        word_count = len(text.split())
        page_count = parsed_data.get("metadata", {}).get("num_pages", 1)
        
        # Ideal: 400-900 words for 1 page, 700-1400 for 2 pages
        if page_count == 1:
            if 400 <= word_count <= 900:
                return 4.0
            elif word_count < 400:
                improvements.append("Resume seems too brief - add more details")
                return 1.5
            else:
                improvements.append("Consider condensing to fit on one page")
                return 2.5
        elif page_count == 2:
            if 700 <= word_count <= 1400:
                return 4.0
            elif word_count < 700:
                improvements.append("For 2 pages, add more content or condense to 1 page")
                return 2.5
            else:
                improvements.append("Resume may be too long - focus on most relevant content")
                return 1.5
        else:
            improvements.append("Keep resume to 1-2 pages maximum")
            return 1.0
    
    # ============ DYNAMIC BONUS METHODS ============
    
    def _check_career_progression(self, experience: List) -> float:
        """Check for career growth (promotions, title progression)"""
        if len(experience) < 2:
            return 0.0
        
        bonus = 0.0
        titles = [exp.get("title", "").lower() for exp in experience if exp.get("title")]
        
        # Check for progression keywords
        senior_keywords = {"senior", "lead", "principal", "staff", "director", "manager", "head", "vp", "chief"}
        mid_keywords = {"ii", "iii", "2", "3", "mid", "experienced"}
        junior_keywords = {"junior", "associate", "entry", "trainee", "intern", "i", "1"}
        
        # Look for progression from junior to senior
        has_junior = any(any(kw in t for kw in junior_keywords) for t in titles[:len(titles)//2+1])
        has_senior = any(any(kw in t for kw in senior_keywords) for t in titles[len(titles)//2:])
        
        if has_junior and has_senior:
            bonus += 5.0  # Clear progression
        elif has_senior:
            bonus += 3.0  # In senior role
        elif len(experience) >= 3:
            bonus += 1.0  # Multiple positions
        
        return min(5.0, bonus)
    
    def _check_certifications(self, text_lower: str, sections: Dict) -> float:
        """Check for valuable certifications"""
        bonus = 0.0
        found_certs = []
        
        for domain, certs in self.valuable_certifications.items():
            for cert in certs:
                if cert in text_lower:
                    found_certs.append(cert)
                    bonus += 1.5
        
        return min(5.0, bonus)
    
    def _check_project_diversity(self, parsed_data: Dict, text_lower: str) -> float:
        """Check for diverse project experience"""
        bonus = 0.0
        
        # Check for projects section
        sections = parsed_data.get("sections", {})
        if "projects" in sections or "project" in text_lower:
            bonus += 1.5
        
        # Check for variety indicators
        variety_keywords = ["microservices", "api", "frontend", "backend", "mobile", 
                           "database", "infrastructure", "cloud", "ml", "ai"]
        found = sum(1 for kw in variety_keywords if kw in text_lower)
        
        if found >= 4:
            bonus += 2.5
        elif found >= 2:
            bonus += 1.0
        
        return min(4.0, bonus)
    
    def _check_modern_skills(self, skills: Dict, text_lower: str) -> float:
        """Check for modern/in-demand skills"""
        bonus = 0.0
        all_skills = skills.get("all_skills", []) if isinstance(skills, dict) else []
        skills_lower = [s.lower() for s in all_skills]
        
        modern_found = sum(1 for s in self.modern_skills if s in text_lower or s in skills_lower)
        
        if modern_found >= 5:
            bonus = 3.0
        elif modern_found >= 3:
            bonus = 2.0
        elif modern_found >= 1:
            bonus = 1.0
        
        return bonus
    
    def _check_leadership(self, text_lower: str, experience: List) -> float:
        """Check for leadership experience"""
        bonus = 0.0
        
        # Check titles
        for exp in experience:
            title = exp.get("title", "").lower()
            if any(kw in title for kw in self.leadership_keywords):
                bonus += 1.5
                break
        
        # Check for leadership in content
        leadership_in_content = sum(1 for kw in self.leadership_keywords if kw in text_lower)
        if leadership_in_content >= 3:
            bonus += 1.5
        
        return min(3.0, bonus)
    
    def _check_industry_keywords(self, text_lower: str) -> float:
        """Check for industry-specific expertise"""
        bonus = 0.0
        best_match = 0
        
        for industry, keywords in self.industry_keywords.items():
            found = sum(1 for kw in keywords if kw in text_lower)
            if found > best_match:
                best_match = found
        
        if best_match >= 5:
            bonus = 3.0
        elif best_match >= 3:
            bonus = 2.0
        elif best_match >= 1:
            bonus = 1.0
        
        return bonus
    
    def _check_international(self, text_lower: str) -> float:
        """Check for international/remote experience"""
        bonus = 0.0
        
        intl_keywords = ["international", "global", "remote", "distributed", "multinational",
                        "cross-cultural", "offshore", "worldwide"]
        found = sum(1 for kw in intl_keywords if kw in text_lower)
        
        if found >= 2:
            bonus = 2.0
        elif found >= 1:
            bonus = 1.0
        
        return bonus
    
    # ============ PENALTY METHODS ============
    
    def _check_employment_gaps(self, experience: List) -> float:
        """Check for unexplained employment gaps"""
        if len(experience) < 2:
            return 0.0
        
        # Would need proper date parsing for accurate gap detection
        # Simplified: just check if there's a gap indicator
        return 0.0  # TODO: Implement proper gap detection
    
    def _check_outdated_skills(self, skills: Dict, text_lower: str) -> float:
        """Check for outdated technologies"""
        penalty = 0.0
        all_skills = skills.get("all_skills", []) if isinstance(skills, dict) else []
        skills_lower = [s.lower() for s in all_skills]
        
        outdated_found = sum(1 for s in self.outdated_skills if s in skills_lower or s in text_lower)
        
        if outdated_found >= 3:
            penalty = 3.0
        elif outdated_found >= 1:
            penalty = 1.5
        
        return penalty
    
    def _check_generic_content(self, text_lower: str) -> float:
        """Check for generic/buzzword-heavy content"""
        penalty = 0.0
        
        generic_phrases = [
            "results-driven", "team player", "hard worker", "detail-oriented",
            "self-starter", "go-getter", "synergy", "think outside the box",
            "dynamic", "proactive", "passionate"
        ]
        
        found = sum(1 for phrase in generic_phrases if phrase in text_lower)
        
        if found >= 4:
            penalty = 3.0
        elif found >= 2:
            penalty = 1.5
        
        return penalty
    
    def _check_impact_statements(self, experience: List, text: str) -> float:
        """Check if achievements show impact"""
        if not experience:
            return 0.0
        
        # Look for impact patterns
        impact_patterns = [
            r'increased\s+\w+\s+by',
            r'reduced\s+\w+\s+by',
            r'improved\s+\w+\s+by',
            r'saved\s+\$?\d+',
            r'generated\s+\$?\d+',
            r'resulting in',
            r'leading to',
        ]
        
        impact_count = sum(len(re.findall(p, text.lower())) for p in impact_patterns)
        
        if impact_count == 0:
            return 2.0  # Penalty for no impact statements
        
        return 0.0
    
    def _calculate_job_relevance(self, parsed_data: Dict, job_description: str, 
                                  target_role: Optional[str] = None) -> float:
        """Calculate relevance to a specific job"""
        if not job_description:
            return 0.0
        
        job_lower = job_description.lower()
        resume_text = parsed_data.get("text", "").lower()
        all_skills = parsed_data.get("skills", {}).get("all_skills", []) if isinstance(parsed_data.get("skills"), dict) else []
        skills_lower = set(s.lower() for s in all_skills)
        
        # Extract job keywords (simple approach)
        job_words = set(re.findall(r'\b[a-z]{3,}\b', job_lower))
        resume_words = set(re.findall(r'\b[a-z]{3,}\b', resume_text))
        
        # Common words to ignore
        stop_words = {"the", "and", "for", "are", "with", "have", "will", "from", "this", "that", "they", "been"}
        job_words -= stop_words
        resume_words -= stop_words
        
        # Calculate overlap
        overlap = len(job_words & resume_words)
        relevance = (overlap / max(len(job_words), 1)) * 100
        
        # Boost for skill matches
        job_skill_matches = sum(1 for skill in skills_lower if skill in job_lower)
        if job_skill_matches >= 5:
            relevance = min(100, relevance + 20)
        elif job_skill_matches >= 3:
            relevance = min(100, relevance + 10)
        
        return min(100.0, relevance)
    
    def _calculate_ats_score(self, parsed_data: Dict, scores: Dict) -> float:
        """Calculate ATS (Applicant Tracking System) compatibility score"""
        ats_score = 0.0
        
        # Text extractable (essential for ATS)
        text = parsed_data.get("text", "")
        if len(text) > 100:
            ats_score += 30.0
        
        # Standard sections
        sections = parsed_data.get("sections", {})
        standard_sections = ["experience", "education", "skills"]
        found = sum(1 for s in standard_sections if s in sections)
        ats_score += found * 15.0  # Up to 45 points
        
        # Contact info
        contact = parsed_data.get("contact_info", {})
        if contact.get("emails"):
            ats_score += 10.0
        if contact.get("phones"):
            ats_score += 5.0
        
        # Not scanned/image-based
        quality = parsed_data.get("quality", {})
        if not quality.get("is_scanned", False):
            ats_score += 10.0
        
        return min(100.0, ats_score)
    
    def _get_grade(self, score: float) -> tuple:
        """Convert score to letter grade"""
        if score >= 90:
            return "A", "Excellent"
        elif score >= 80:
            return "A-", "Very Good"
        elif score >= 70:
            return "B+", "Good"
        elif score >= 60:
            return "B", "Above Average"
        elif score >= 50:
            return "C+", "Average"
        elif score >= 40:
            return "C", "Below Average"
        elif score >= 30:
            return "D", "Needs Work"
        else:
            return "F", "Poor"
    
    def _generate_summary(self, score: float, grade: str, missing: List, exp_count: int,
                          bonuses: List, penalties: List) -> str:
        """Generate one-line summary with dynamic context"""
        bonus_count = len(bonuses)
        penalty_count = len(penalties)
        
        if score >= 85:
            return f"Outstanding resume! {exp_count} positions, {bonus_count} bonus factors detected."
        elif score >= 75:
            if bonuses:
                return f"Strong resume with notable strengths. {bonus_count} bonus points earned."
            return f"Strong resume with {exp_count} positions. Consider adding more impact metrics."
        elif score >= 65:
            if missing:
                return f"Good resume with room for improvement. Missing: {', '.join(missing[:2])}."
            if penalties:
                return f"Good resume. Address: {penalties[0].split(':')[0]}."
            return f"Good resume. Add more quantified achievements for higher score."
        elif score >= 50:
            if missing:
                return f"Average resume. Add: {', '.join(missing[:2])}."
            return f"Average resume. Focus on adding metrics and reducing generic content."
        else:
            if missing:
                return f"Resume needs work. Critical missing: {', '.join(missing)}."
            return f"Resume needs significant improvement in content and structure."
    
    def _prioritize_improvements(self, improvements: List, scores: Dict) -> List:
        """Sort improvements by impact (lowest scoring areas first)"""
        # Simple prioritization based on score gaps
        priority_map = {
            "Email": 100,
            "phone": 90,
            "Professional Summary": 85,
            "experience": 80,
            "Skills": 75,
            "Education": 70,
            "dates": 65,
            "metrics": 60,
            "action verbs": 55,
            "LinkedIn": 40,
            "categories": 30,
        }
        
        def get_priority(imp: str) -> int:
            for key, priority in priority_map.items():
                if key.lower() in imp.lower():
                    return priority
            return 50
        
        return sorted(improvements, key=get_priority, reverse=True)
    
    def _identify_strengths(self, scores: Dict) -> List[str]:
        """Identify strongest areas"""
        # This is handled during scoring now
        return []
    
    def _identify_weaknesses(self, scores: Dict) -> List[str]:
        """Identify weakest areas"""
        # This is handled during scoring now
        return []


# Quick test function
def test_scorer():
    """Test the enhanced scorer"""
    scorer = EnhancedQualityScorer()
    
    # Sample parsed resume
    sample = {
        "text": """
        John Doe
        john.doe@gmail.com | 555-123-4567 | linkedin.com/in/johndoe
        
        PROFESSIONAL SUMMARY
        Experienced software engineer with 5+ years building scalable applications.
        
        EXPERIENCE
        Senior Developer at Tech Corp
        2020 - Present
        • Led team of 5 engineers, increasing productivity by 30%
        • Developed microservices handling 1M+ requests/day
        
        SKILLS
        Python, JavaScript, AWS, Docker, React
        
        EDUCATION
        B.S. Computer Science, State University
        GPA: 3.8
        """,
        "sections": {
            "summary": {"content": "Experienced software engineer with 5+ years building scalable applications."},
            "experience": {"content": "Senior Developer at Tech Corp..."},
            "skills": {"content": "Python, JavaScript, AWS, Docker, React"},
            "education": {"content": "B.S. Computer Science, State University GPA: 3.8"}
        },
        "contact_info": {
            "emails": ["john.doe@gmail.com"],
            "phones": ["555-123-4567"],
            "linkedin": "linkedin.com/in/johndoe"
        },
        "experience": [
            {
                "title": "Senior Developer",
                "company": "Tech Corp",
                "start_date": "2020-01-01",
                "achievements": ["Led team of 5 engineers", "Developed microservices"]
            }
        ],
        "skills": {
            "all_skills": ["Python", "JavaScript", "AWS", "Docker", "React"],
            "by_category": {
                "technical": ["Python", "JavaScript", "AWS", "Docker", "React"],
                "soft": []
            }
        },
        "metadata": {"num_pages": 1}
    }
    
    result = scorer.score_resume(sample)
    print("="*60)
    print("RESUME QUALITY SCORE")
    print("="*60)
    print(f"\nScore: {result.score}/100")
    print(f"Grade: {result.grade} ({result.tier})")
    print(f"ATS Score: {result.ats_score}/100")
    print(f"\nSummary: {result.summary}")
    print(f"\nStrengths: {', '.join(result.strengths)}")
    print(f"\nTo Improve: {', '.join(result.improvements)}")
    if result.missing:
        print(f"\nMissing: {', '.join(result.missing)}")
    

if __name__ == "__main__":
    test_scorer()
