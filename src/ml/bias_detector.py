"""
Bias Detection & Mitigation (rule-based)

This module does NOT attempt to infer protected attributes (race, gender, age) about candidates.
Instead it scans text (resumes, job descriptions, model outputs) for potentially biased or exclusionary
language and returns flagged items plus suggested neutral rewrites and mitigation guidance.

Outputs:
- flags: list of {type, span_text, context, reason}
- rewrites: list of suggested neutral alternatives
- guidance: general best-practice suggestions

Safe design notes:
- Rule-based patterns only (no demographic inference)
- Provide educational guidance and neutral rewrite suggestions
"""

import re
from typing import List, Dict, Any, Tuple


class BiasDetector:
    def __init__(self):
        # Patterns for biased or exclusionary phrasing (case-insensitive)
        self.patterns = [
            # Gendered words in job ads
            (re.compile(r"\b(ninja|rockstar|guru|hacker|wizard|superstar)\b", re.I), 'gendered_or_culture'),
            (re.compile(r"\b(he/him|she/her|they/them)\b", re.I), 'gender_pronouns_explicit'),
            (re.compile(r"\b(manage|sales)\b", re.I), 'neutral'),

            # Gender-coded adjectives (traditionally masculine/feminine)
            (re.compile(r"\b(assertive|dominant|driven|ambitious|competitive|confident)\b", re.I), 'possibly_masculine'),
            (re.compile(r"\b(understanding|communal|supportive|interpersonal|loyal)\b", re.I), 'possibly_feminine'),

            # Age references
            (re.compile(r"\b(recent graduate|young|fresh graduate|new grad)\b", re.I), 'age_bias_early_career'),
            (re.compile(r"\b(over \d{2}|under \d{2}|mid[- ]?\d{2}s|forties|fifties|sixties)\b", re.I), 'age_reference'),

            # Disability/ability phrasing
            (re.compile(r"\b(able[- ]bodied|physically fit|must be able to)\b", re.I), 'ability_bias'),

            # Nationality / language requirements that may be exclusionary
            (re.compile(r"\b(native English speaker\b|must be fluent in English)", re.I), 'language_requirement'),

            # Unnecessary educational requirement phrasing
            (re.compile(r"\b(bachelor'?s degree|master'?s degree)\b\s*(in)?", re.I), 'education_requirement'),

            # Culturally loaded or aggressive buzzwords
            (re.compile(r"\b(passionate about|obsessed with|must be obsessed)\b", re.I), 'culture_tone'),

            # Sexual/relationship status or family status
            (re.compile(r"\b(married|single|husband|wife|pregnant|maternity|paternity)\b", re.I), 'family_status'),

            # Gendered role examples
            (re.compile(r"\b(assistant|receptionist|nurse|secretary)\b", re.I), 'gendered_role_may_warn'),

            # Phrases that encourage discrimination by experience phrasing
            (re.compile(r"\b(young and energetic|recent grad|digital native)\b", re.I), 'experience_wording')
        ]

        # Neutral rewrite suggestions mapping (simple substitutions / guidance)
        self.rewrite_map = {
            'ninja': 'experienced',
            'rockstar': 'experienced',
            'guru': 'experienced',
            'wizard': 'experienced',
            'superstar': 'experienced',
            'young': 'early-career',
            'recent graduate': 'early-career candidates or equivalent experience',
            'new grad': 'early-career candidates or equivalent experience',
            'must be fluent in english': 'strong written and verbal communication skills in English preferred',
            'native english speaker': 'proficiency in English preferred',
            'able-bodied': 'able to perform the essential functions of the role with or without reasonable accommodation'
        }

        # Guidance snippets
        self.guidance = [
            'Avoid gendered or overly aggressive words (e.g., "rockstar", "ninja"). Use neutral descriptors like "experienced" or list skills explicitly.',
            'When possible, allow "equivalent experience" instead of strict degree requirements to avoid excluding skilled candidates without degrees.',
            'Avoid age-specific phrasing such as "recent graduate" or references to age ranges.',
            'Do not require "native" language speakers unless the role legitimately requires local cultural knowledge; prefer "proficiency in <language>".',
            'Replace vague culture-fit requirements with specific behaviors and competencies (e.g., collaboration, communication, ownership).',
            'Consider adding an accommodations statement to show willingness to support candidates with disabilities.'
        ]

    def scan_text(self, text: str, context: Dict[str, str] = None) -> Dict[str, Any]:
        """Scan input text and return flags, suggested rewrites and guidance.
        context: optional dict with metadata like {'type':'job_description'|'resume','source':'job_posting'}
        """
        if not text:
            return {'flags':[], 'rewrites':[], 'guidance': self.guidance}

        flags = []
        rewrites = []

        # search for patterns
        for pattern, ptype in self.patterns:
            for m in pattern.finditer(text):
                span = m.group(0)
                start, end = m.span()
                reason = self._reason_for_type(ptype)
                flags.append({
                    'type': ptype,
                    'span_text': span,
                    'start': start,
                    'end': end,
                    'reason': reason,
                    'context': context or {}
                })

                # build rewrite if possible
                rewrite = self._suggest_rewrite(span)
                if rewrite:
                    rewrites.append({
                        'original': span,
                        'suggested': rewrite,
                        'note': f"Consider replacing '{span}' with '{rewrite}' to reduce potential bias."
                    })

        # deduplicate flags by span_text
        unique_flags = []
        seen = set()
        for f in flags:
            key = (f['span_text'].lower(), f['type'])
            if key not in seen:
                unique_flags.append(f)
                seen.add(key)

        # canonicalize rewrites
        unique_rewrites = []
        seen_r = set()
        for r in rewrites:
            key = (r['original'].lower(), r['suggested'].lower())
            if key not in seen_r:
                unique_rewrites.append(r)
                seen_r.add(key)

        return {
            'flags': unique_flags,
            'rewrites': unique_rewrites,
            'guidance': self.guidance
        }

    def _reason_for_type(self, ptype: str) -> str:
        reasons = {
            'gendered_or_culture': 'Culturally loaded or slang phrase; may discourage some applicants.',
            'gender_pronouns_explicit': 'Explicit pronouns may signal gender preference.',
            'possibly_masculine': 'Adjectives associated with masculine-coded language; may deter female applicants.',
            'possibly_feminine': 'Adjectives associated with feminine-coded language; may signal stereotypes.',
            'age_bias_early_career': 'Age-related phrasing focusing on early-career applicants.',
            'age_reference': 'Age references can be discriminatory.',
            'ability_bias': 'Phrasing may exclude candidates with disabilities.',
            'language_requirement': 'May exclude non-native speakers; consider rephrasing.',
            'education_requirement': 'Unqualified degree requirement may exclude skilled candidates without degrees; consider equivalent experience.',
            'culture_tone': 'Aggressive or cult-like language; consider neutral tone.',
            'family_status': 'Personal family status references are irrelevant to job performance.',
            'gendered_role_may_warn': 'Certain roles are historically gendered; review wording to avoid stereotype reinforcement.',
            'experience_wording': 'Potentially exclusionary phrasing for experience or cultural background.'
        }
        return reasons.get(ptype, 'Potentially problematic phrasing')

    def _suggest_rewrite(self, span: str) -> str:
        key = span.lower()
        # exact match map
        if key in self.rewrite_map:
            return self.rewrite_map[key]
        # fuzzy checks
        if 'rockstar' in key or 'ninja' in key or 'guru' in key:
            return 'experienced professional with proven skills'
        if 'recent graduate' in key or 'new grad' in key:
            return 'early-career candidates or equivalent experience'
        if 'must be fluent in english' in key or 'native english speaker' in key:
            return 'proficiency in English is preferred; specify required level (e.g., professional working proficiency)'
        if 'able-bodied' in key:
            return 'able to perform essential job functions with or without reasonable accommodation'
        return ''


# ================= SELF-TEST =================
if __name__ == '__main__':
    detector = BiasDetector()

    sample_job = """
    We are looking for a rockstar developer (he/him) who is a recent graduate or young and energetic. Must be a native English speaker. Bachelor\'s degree required. Passionate and obsessed candidates preferred. Must be able to lift 50 lbs and be able-bodied.
    """

    sample_resume = """
    Experienced software developer. Strong communicator. Married with two kids. Worked on multiple projects. Passionate about code and obsessed with performance.
    """

    print('\nScanning job posting:')
    out_job = detector.scan_text(sample_job, context={'type':'job_description'})
    print('Flags:')
    for f in out_job['flags']:
        print('-', f['span_text'], '->', f['reason'])
    print('\nRewrites:')
    for r in out_job['rewrites']:
        print('-', r['original'], '=>', r['suggested'])

    print('\n---\nScanning resume:')
    out_res = detector.scan_text(sample_resume, context={'type':'resume'})
    print('Flags:')
    for f in out_res['flags']:
        print('-', f['span_text'], '->', f['reason'])
    print('\nRewrites:')
    for r in out_res['rewrites']:
        print('-', r['original'], '=>', r['suggested'])

    print('\nGuidance:')
    for g in out_res['guidance']:
        print('-', g)
