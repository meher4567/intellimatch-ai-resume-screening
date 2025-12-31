"""
ML Components for IntelliMatch AI
Hybrid ML + Rule-Based Extraction System

Uses lazy loading to avoid importing heavy dependencies (torch, sentence_transformers)
until they're actually needed.
"""

# Lazy loading implementation to avoid heavy imports at module level
def __getattr__(name):
    """Lazy import of ML components to avoid loading torch/sentence_transformers upfront"""
    if name == 'NERExtractor':
        from .ner_extractor import NERExtractor
        return NERExtractor
    elif name == 'SkillEmbedder':
        from .skill_embedder import SkillEmbedder
        return SkillEmbedder
    elif name == 'HybridNameExtractor':
        from .hybrid_name_extractor import HybridNameExtractor
        return HybridNameExtractor
    elif name == 'OrganizationExtractor':
        from .organization_extractor import OrganizationExtractor
        return OrganizationExtractor
    elif name == 'DynamicSkillExtractor':
        from .dynamic_skill_extractor import DynamicSkillExtractor
        return DynamicSkillExtractor
    elif name == 'extract_skills_from_text':
        from .dynamic_skill_extractor import extract_skills_from_text
        return extract_skills_from_text
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ['NERExtractor', 'SkillEmbedder', 'HybridNameExtractor', 'OrganizationExtractor', 
           'DynamicSkillExtractor', 'extract_skills_from_text']
