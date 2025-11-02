"""
Semantic Skill Extractor using Embeddings
Extracts skills using semantic similarity, not just keyword matching
"""

from typing import List, Set, Dict, Tuple, Optional
import logging
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
import numpy as np
import re
import json
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class SkillMatch:
    """Represents a matched skill with confidence"""
    skill: str
    confidence: float
    matched_text: str
    category: Optional[str] = None


class SkillEmbedder:
    """
    Semantic skill extractor using sentence embeddings
    
    Features:
    - Semantic similarity matching (finds "ML" when resume says "machine learning")
    - Skill normalization (maps variations to canonical forms)
    - Category-based organization
    - Hybrid: Combines exact matching + semantic matching
    """
    
    # Comprehensive skill database with categories
    SKILL_DATABASE = {
        # Programming Languages
        'programming': [
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C', 'C#',
            'Go', 'Rust', 'Ruby', 'PHP', 'Swift', 'Kotlin', 'Scala',
            'R', 'MATLAB', 'Perl', 'Shell', 'Bash', 'PowerShell',
            'SQL', 'PL/SQL', 'T-SQL', 'HTML', 'CSS', 'SASS', 'LESS'
        ],
        
        # Frameworks & Libraries
        'frameworks': [
            'React', 'Angular', 'Vue.js', 'Next.js', 'Nuxt.js', 'Svelte',
            'Django', 'Flask', 'FastAPI', 'Spring Boot', 'Spring', 'Express.js',
            'Node.js', 'ASP.NET', '.NET Core', 'Laravel', 'Ruby on Rails',
            'TensorFlow', 'PyTorch', 'Keras', 'Scikit-learn', 'Pandas', 'NumPy',
            'jQuery', 'Bootstrap', 'Tailwind CSS', 'Material-UI', 'Ant Design'
        ],
        
        # ML/AI/Data Science
        'ml_ai': [
            'Machine Learning', 'Deep Learning', 'Neural Networks', 'CNN', 'RNN', 'LSTM',
            'Natural Language Processing', 'NLP', 'Computer Vision', 'Reinforcement Learning',
            'Transfer Learning', 'Fine-tuning', 'Model Training', 'Model Deployment',
            'Feature Engineering', 'Data Analysis', 'Data Visualization', 'Statistics',
            'A/B Testing', 'Hypothesis Testing', 'Time Series Analysis',
            'BERT', 'GPT', 'Transformer', 'LLM', 'Large Language Models'
        ],
        
        # Cloud & DevOps
        'cloud_devops': [
            'AWS', 'Azure', 'Google Cloud', 'GCP', 'Docker', 'Kubernetes',
            'CI/CD', 'Jenkins', 'GitHub Actions', 'GitLab CI', 'CircleCI',
            'Terraform', 'Ansible', 'Chef', 'Puppet', 'CloudFormation',
            'Lambda', 'EC2', 'S3', 'ECS', 'EKS', 'Azure Functions',
            'Microservices', 'Serverless', 'Container Orchestration'
        ],
        
        # Databases
        'databases': [
            'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Cassandra',
            'DynamoDB', 'Oracle', 'SQL Server', 'SQLite', 'MariaDB',
            'Elasticsearch', 'Neo4j', 'CouchDB', 'Firebase', 'Firestore',
            'Vector Database', 'FAISS', 'Pinecone', 'ChromaDB'
        ],
        
        # Tools & Technologies
        'tools': [
            'Git', 'GitHub', 'GitLab', 'Bitbucket', 'SVN',
            'JIRA', 'Confluence', 'Trello', 'Asana', 'Slack',
            'VS Code', 'IntelliJ', 'PyCharm', 'Eclipse', 'Vim',
            'Jupyter', 'Postman', 'Swagger', 'Figma', 'Adobe XD',
            'Linux', 'Unix', 'Windows', 'macOS', 'Ubuntu'
        ],
        
        # Soft Skills
        'soft_skills': [
            'Leadership', 'Communication', 'Team Collaboration', 'Problem Solving',
            'Project Management', 'Agile', 'Scrum', 'Kanban', 'Critical Thinking',
            'Time Management', 'Adaptability', 'Creativity', 'Public Speaking'
        ]
    }
    
    # Skill variations/aliases
    SKILL_ALIASES = {
        'ML': 'Machine Learning',
        'DL': 'Deep Learning',
        'JS': 'JavaScript',
        'TS': 'TypeScript',
        'K8s': 'Kubernetes',
        'K8': 'Kubernetes',
        'NLP': 'Natural Language Processing',
        'CV': 'Computer Vision',
        'CI/CD': 'Continuous Integration',
        'AWS': 'Amazon Web Services',
        'GCP': 'Google Cloud Platform',
        'AI': 'Artificial Intelligence',
        'DB': 'Database',
    }
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", similarity_threshold: float = 0.7):
        """
        Initialize skill embedder
        
        Args:
            model_name: Sentence transformer model to use
            similarity_threshold: Minimum cosine similarity for semantic match
        """
        logger.info(f"Loading sentence transformer model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.similarity_threshold = similarity_threshold
        
        # Flatten skill database
        self.all_skills = []
        self.skill_categories = {}
        for category, skills in self.SKILL_DATABASE.items():
            for skill in skills:
                self.all_skills.append(skill)
                self.skill_categories[skill.lower()] = category
        
        # Pre-compute embeddings for all skills (cache)
        logger.info(f"Computing embeddings for {len(self.all_skills)} skills...")
        self.skill_embeddings = self.model.encode(self.all_skills, convert_to_numpy=True)
        logger.info("Skill embeddings ready!")
    
    def extract_skills_hybrid(self, text: str, top_k: int = 50) -> List[SkillMatch]:
        """
        Extract skills using hybrid approach: exact matching + semantic matching
        
        Args:
            text: Resume text
            top_k: Maximum number of skills to return
            
        Returns:
            List of SkillMatch objects sorted by confidence
        """
        # Step 1: Exact matching (fast, high precision)
        exact_matches = self._extract_exact_matches(text)
        
        # Step 2: Semantic matching (slower, finds variations)
        semantic_matches = self._extract_semantic_matches(text)
        
        # Step 3: Merge and deduplicate
        all_matches = self._merge_matches(exact_matches, semantic_matches)
        
        # Step 4: Sort by confidence and return top k
        all_matches.sort(key=lambda x: x.confidence, reverse=True)
        
        return all_matches[:top_k]
    
    def _extract_exact_matches(self, text: str) -> List[SkillMatch]:
        """
        Extract skills using exact keyword matching
        Fast and high precision
        """
        text_lower = text.lower()
        matches = []
        
        for skill in self.all_skills:
            # Create regex pattern for whole word matching
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            
            if re.search(pattern, text_lower):
                matches.append(SkillMatch(
                    skill=skill,
                    confidence=1.0,  # Exact match = high confidence
                    matched_text=skill,
                    category=self.skill_categories.get(skill.lower())
                ))
        
        # Also check aliases
        for alias, full_name in self.SKILL_ALIASES.items():
            pattern = r'\b' + re.escape(alias.lower()) + r'\b'
            if re.search(pattern, text_lower):
                matches.append(SkillMatch(
                    skill=full_name,
                    confidence=0.95,  # Alias = slightly lower confidence
                    matched_text=alias,
                    category=self.skill_categories.get(full_name.lower())
                ))
        
        return matches
    
    def _extract_semantic_matches(self, text: str) -> List[SkillMatch]:
        """
        Extract skills using semantic similarity
        Finds skills mentioned differently (e.g., "building ML models" → "Machine Learning")
        """
        # Extract candidate phrases from text (2-5 word ngrams)
        candidates = self._extract_candidate_phrases(text)
        
        if not candidates:
            return []
        
        # Encode candidates
        candidate_embeddings = self.model.encode(candidates, convert_to_numpy=True)
        
        # Compute cosine similarity with all skills
        similarities = np.dot(candidate_embeddings, self.skill_embeddings.T)
        
        matches = []
        seen_skills = set()
        
        for i, candidate in enumerate(candidates):
            # Find best matching skill for this candidate
            best_idx = np.argmax(similarities[i])
            best_score = similarities[i][best_idx]
            
            if best_score >= self.similarity_threshold:
                skill = self.all_skills[best_idx]
                
                # Avoid duplicates
                if skill not in seen_skills:
                    matches.append(SkillMatch(
                        skill=skill,
                        confidence=float(best_score),
                        matched_text=candidate,
                        category=self.skill_categories.get(skill.lower())
                    ))
                    seen_skills.add(skill)
        
        return matches
    
    def _extract_candidate_phrases(self, text: str, max_phrases: int = 200) -> List[str]:
        """
        Extract candidate phrases that might be skills
        Focus on noun phrases, technical terms
        """
        # Simple approach: extract 2-5 word ngrams
        words = re.findall(r'\b[A-Za-z][A-Za-z0-9+#./-]*\b', text)
        
        candidates = []
        
        # Extract ngrams
        for n in range(1, 6):  # 1 to 5 words
            for i in range(len(words) - n + 1):
                phrase = ' '.join(words[i:i+n])
                
                # Filter: skip very common words, too long phrases
                if len(phrase) > 50 or len(phrase) < 2:
                    continue
                
                # Skip if all lowercase (likely common words)
                if phrase.islower() and n == 1:
                    continue
                
                candidates.append(phrase)
        
        # Limit candidates to avoid slowdown
        return candidates[:max_phrases]
    
    def _merge_matches(self, exact: List[SkillMatch], semantic: List[SkillMatch]) -> List[SkillMatch]:
        """
        Merge exact and semantic matches, removing duplicates
        Prefer exact matches (higher confidence)
        """
        merged = {}
        
        # Add exact matches first (higher priority)
        for match in exact:
            merged[match.skill.lower()] = match
        
        # Add semantic matches only if not already found
        for match in semantic:
            skill_key = match.skill.lower()
            if skill_key not in merged:
                merged[skill_key] = match
            elif merged[skill_key].confidence < match.confidence:
                # Update if semantic match has higher confidence
                merged[skill_key] = match
        
        return list(merged.values())
    
    def categorize_skills(self, matches: List[SkillMatch]) -> Dict[str, List[str]]:
        """
        Organize skills by category
        
        Returns:
            Dict mapping category to list of skills
        """
        categorized = {}
        
        for match in matches:
            category = match.category or 'other'
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(match.skill)
        
        return categorized
    
    def get_skill_stats(self, matches: List[SkillMatch]) -> Dict:
        """
        Get statistics about extracted skills
        """
        return {
            'total_skills': len(matches),
            'exact_matches': sum(1 for m in matches if m.confidence >= 0.95),
            'semantic_matches': sum(1 for m in matches if m.confidence < 0.95),
            'avg_confidence': sum(m.confidence for m in matches) / len(matches) if matches else 0,
            'categories': len(set(m.category for m in matches if m.category)),
            'by_category': {
                cat: len(skills) 
                for cat, skills in self.categorize_skills(matches).items()
            }
        }
    
    def calculate_similarity(self, skill1: str, skill2: str) -> float:
        """
        Calculate semantic similarity between two skills
        
        Args:
            skill1: First skill
            skill2: Second skill
            
        Returns:
            Similarity score (0-1)
        """
        # Encode both skills
        embeddings = self.model.encode([skill1, skill2], convert_to_numpy=True)
        
        # Calculate cosine similarity
        similarity = np.dot(embeddings[0], embeddings[1]) / (
            np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
        )
        
        return float(similarity)


# Convenience function
def extract_skills_from_text(text: str) -> List[str]:
    """
    Simple interface: extract skills and return list of skill names
    """
    embedder = SkillEmbedder()
    matches = embedder.extract_skills_hybrid(text)
    return [m.skill for m in matches]
