"""
Multi-language Support (Spanish, French) - Rule-based

Provides simple utilities to detect section headers and extract skill-like tokens
from resume text written in English, Spanish or French. Designed as a safe, rule-based
fallback to provide useful analyses without requiring ML models or embeddings.

Functions:
- detect_language_short(text) -> 'en'|'es'|'fr'|'unknown'
- extract_sections(text, lang='auto') -> dict of {section_name: text}
- extract_skill_candidates(text, lang='auto') -> list of candidate skill tokens

This is intentionally lightweight and deterministic for reliability.
"""

import re
from typing import Dict, List, Tuple

# Common headers in each language (lowercase)
SECTION_HEADERS = {
    'en': {
        'summary': [r'summary', r'professional summary', r'objective'],
        'skills': [r'skills', r'technical skills', r'core skills'],
        'experience': [r'work experience', r'experience', r'employment history', r'professional experience'],
        'education': [r'education', r'qualifications', r'educational background'],
        'projects': [r'projects', r'personal projects', r'open source'],
        'certifications': [r'certifications', r'licenses']
    },
    'es': {
        'summary': [r'resumen profesional', r'perfil profesional', r'perfil'],
        'skills': [r'habilidades', r'competencias', r'habilidades técnicas'],
        'experience': [r'experiencia laboral', r'experiencia', r'historial laboral'],
        'education': [r'educación', r'formación', r'formación académica'],
        'projects': [r'proyectos', r'proyectos personales'],
        'certifications': [r'certificaciones', r'títulos']
    },
    'fr': {
        'summary': [r'profil professionnel', r'resumé professionnel', r'profil'],
        'skills': [r'compétences', r'compétences techniques', r'skills'],
        'experience': [r'expérience professionnelle', r'expérience', r'historique professionnel'],
        'education': [r'études', r'formation', r'diplômes'],
        'projects': [r'projets', r'projets personnels'],
        'certifications': [r'certifications', r'attestations']
    }
}

# Simple language detection keywords
LANGUAGE_KEYWORDS = {
    'es': [r'\b(en|el|la|los|las|y|con|para|experiencia|proyectos)\b'],
    'fr': [r'\b(le|la|les|et|pour|avec|expérience|projets|compétences)\b']
}

# Simple skill token extractor patterns (multi-lingual friendly): look for capitalized terms or known tech words
COMMON_TECH = [
    'python','java','javascript','react','angular','aws','docker','kubernetes','sql','postgresql','mongodb','tensorflow','pytorch','nlp','spark','hadoop'
]

SKILL_PATTERN = re.compile(r"\b([A-Za-z+#\.]{2,30})\b")


def detect_language_short(text: str) -> str:
    """Return 'es' or 'fr' or 'en' or 'unknown' using lightweight heuristics."""
    if not text or not text.strip():
        return 'unknown'
    lower = text.lower()
    es_score = 0
    fr_score = 0
    for p in LANGUAGE_KEYWORDS.get('es', []):
        if re.search(p, lower):
            es_score += 1
    for p in LANGUAGE_KEYWORDS.get('fr', []):
        if re.search(p, lower):
            fr_score += 1
    if es_score > fr_score and es_score >= 1:
        return 'es'
    if fr_score > es_score and fr_score >= 1:
        return 'fr'
    # fallback: check for many ASCII english headers
    en_indicators = ['experience','skills','education','projects','summary']
    en_hits = sum(1 for w in en_indicators if w in lower)
    if en_hits >= 2:
        return 'en'
    return 'unknown'


def extract_sections(text: str, lang: str = 'auto') -> Dict[str, str]:
    """Identify sections and return mapping section_name -> section text.
    If lang='auto' the detector will pick a language.
    """
    if lang == 'auto':
        lang = detect_language_short(text)
        if lang == 'unknown':
            lang = 'en'
    headers = SECTION_HEADERS.get(lang, SECTION_HEADERS['en'])

    # Find header positions
    lower = text.lower()
    positions: List[Tuple[int,str]] = []
    for sec, patterns in headers.items():
        for pat in patterns:
            for m in re.finditer(pat, lower):
                positions.append((m.start(), sec))
    positions.sort()

    sections: Dict[str, str] = {}
    if not positions:
        # No headers found; return whole text as 'body'
        sections['body'] = text.strip()
        return sections

    # Extract between header positions
    for i, (pos, sec) in enumerate(positions):
        start = pos
        end = positions[i+1][0] if i+1 < len(positions) else len(text)
        snippet = text[start:end].strip()
        # remove header word from snippet start
        # find header label occurrence and strip it
        first_line = snippet.split('\n',1)[0]
        # remove only the header token
        cleaned = re.sub(r'^\s*\w[\w\s-]{0,40}\n?', '', snippet, count=1)
        sections[sec] = cleaned.strip() if cleaned.strip() else snippet

    return sections


def extract_skill_candidates(text: str, lang: str = 'auto') -> List[str]:
    """Return a list of probable skill tokens from text. Language used for heuristics if needed."""
    if not text:
        return []
    lower = text.lower()
    # First, find known tech words
    found = []
    for tech in COMMON_TECH:
        if tech in lower and tech not in found:
            found.append(tech)
    # Extract capitalized tokens as candidates (names like Django, React)
    # But allow multi-language, so pick tokens that look like tech (letters/numbers/+#.)
    for m in SKILL_PATTERN.finditer(text):
        token = m.group(1).strip()
        token_low = token.lower()
        if token_low in found:
            continue
        # heuristics: if token contains mixed-case or known suffixes
        if token[0].isupper() or token_low in ['sql','nosql','api','rest'] or re.search(r'\b\w+(?:js|sql|db|api)\b', token_low):
            # filter out common stopwords that match pattern
            if token_low not in ['and','the','for','with','that','this','from'] and len(token) > 1:
                found.append(token)
    # normalization: unique, keep original casing where possible
    normalized = []
    seen = set()
    for t in found:
        key = t.lower()
        if key not in seen:
            normalized.append(t)
            seen.add(key)
    return normalized


# ================= SELF-TEST =================
if __name__ == '__main__':
    sample_en = """
    Professional Summary\nExperienced backend engineer with expertise in Python, Django and AWS.\n\nSkills\nPython, Django, PostgreSQL, AWS, Docker\n\nExperience\nCompany A - Senior Software Engineer (2019-2024)\n- Built microservices using Docker and Kubernetes\n"""

    sample_es = """
    Perfil Profesional\nIngeniero de software con experiencia en Python y AWS.\n\nHabilidades\nPython, Django, AWS, Docker\n\nExperiencia Laboral\nEmpresa X - Ingeniero de Software (2018-2023)\n- Desarrollo de microservicios y despliegue en la nube\n"""

    sample_fr = """
    Profil Professionnel\nIngénieur backend spécialisé en Python et AWS.\n\nCompétences\nPython, Django, AWS, Docker\n\nExpérience Professionnelle\nSociété Y - Ingénieur Logiciel (2017-2022)\n- Conception de microservices et déploiement cloud\n"""

    print('Detect language (EN):', detect_language_short(sample_en))
    print('Sections (EN):', list(extract_sections(sample_en).keys()))
    print('Skills (EN):', extract_skill_candidates(sample_en))

    print('\nDetect language (ES):', detect_language_short(sample_es))
    print('Sections (ES):', list(extract_sections(sample_es).keys()))
    print('Skills (ES):', extract_skill_candidates(sample_es))

    print('\nDetect language (FR):', detect_language_short(sample_fr))
    print('Sections (FR):', list(extract_sections(sample_fr).keys()))
    print('Skills (FR):', extract_skill_candidates(sample_fr))
