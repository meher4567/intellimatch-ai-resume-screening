"""
Tests for ESCO Skills Integration

Tests the ESCOSkillMapper and SkillValidator classes
"""

import pytest
import json
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ml.esco_skill_mapper import ESCOSkillMapper, SkillValidator


# Sample ESCO data for testing
SAMPLE_ESCO_DATA = {
    "skills": [
        {
            "id": "ESCO_001",
            "name": "Python Programming",
            "category": "Programming Languages",
            "aliases": ["Python", "python3"]
        },
        {
            "id": "ESCO_002",
            "name": "JavaScript",
            "category": "Programming Languages",
            "aliases": ["JS", "ECMAScript"]
        },
        {
            "id": "ESCO_003",
            "name": "Machine Learning",
            "category": "Technical Skills",
            "aliases": ["ML", "AI"]
        },
        {
            "id": "ESCO_004",
            "name": "React.js",
            "category": "Web Frameworks",
            "aliases": ["React", "ReactJS"]
        },
        {
            "id": "ESCO_005",
            "name": "SQL",
            "category": "Databases",
            "aliases": ["MySQL", "PostgreSQL"]
        }
    ]
}


@pytest.fixture
def temp_esco_file(tmp_path):
    """Create temporary ESCO skills file"""
    esco_file = tmp_path / "test_esco_skills.json"
    with open(esco_file, 'w') as f:
        json.dump(SAMPLE_ESCO_DATA, f)
    return str(esco_file)


@pytest.fixture
def mapper(temp_esco_file):
    """Create ESCOSkillMapper instance"""
    return ESCOSkillMapper(temp_esco_file)


@pytest.fixture
def validator(mapper):
    """Create SkillValidator instance"""
    return SkillValidator(mapper)


class TestESCOSkillMapper:
    """Test ESCOSkillMapper functionality"""
    
    def test_initialization(self, mapper):
        """Test mapper initializes correctly"""
        assert len(mapper.esco_skills) == 5
        assert 'python programming' in mapper.esco_skills
        assert 'javascript' in mapper.esco_skills
    
    def test_exact_match(self, mapper):
        """Test exact skill matching"""
        result = mapper.map_skill("Python Programming")
        assert result is not None
        assert result['esco_skill'] == "Python Programming"
        assert result['confidence'] == 1.0
        assert result['match_type'] == 'exact'
    
    def test_case_insensitive_match(self, mapper):
        """Test case-insensitive matching"""
        result = mapper.map_skill("python programming")
        assert result is not None
        assert result['esco_skill'] == "Python Programming"
    
    def test_variant_match(self, mapper):
        """Test variant/alias matching"""
        # Test alias
        result = mapper.map_skill("Python")
        assert result is not None
        assert result['esco_skill'] == "Python Programming"
        assert result['match_type'] == 'variant'
        assert result['confidence'] >= 0.9
        
        # Test JS alias
        result = mapper.map_skill("JS")
        assert result is not None
        assert result['esco_skill'] == "JavaScript"
    
    def test_fuzzy_match(self, mapper):
        """Test fuzzy matching for typos"""
        result = mapper.map_skill("Pythoon", threshold=0.7)
        assert result is not None
        assert result['esco_skill'] == "Python Programming"
        assert result['match_type'] == 'fuzzy'
        assert result['confidence'] < 1.0
    
    def test_no_match(self, mapper):
        """Test when no match found"""
        result = mapper.map_skill("NonexistentSkill")
        assert result is None
    
    def test_batch_mapping(self, mapper):
        """Test mapping multiple skills"""
        skills = ["Python", "JavaScript", "React", "InvalidSkill"]
        results = mapper.map_skills_batch(skills)
        
        assert len(results) == 3  # InvalidSkill filtered out
        assert results[0]['esco_skill'] == "Python Programming"
        assert results[1]['esco_skill'] == "JavaScript"
        assert results[2]['esco_skill'] == "React.js"
    
    def test_is_valid_skill(self, mapper):
        """Test skill validation"""
        assert mapper.is_valid_skill("Python") is True
        assert mapper.is_valid_skill("JavaScript") is True
        assert mapper.is_valid_skill("InvalidSkill") is False
    
    def test_filter_valid_skills(self, mapper):
        """Test filtering to valid skills only"""
        skills = ["Python", "InvalidSkill1", "JavaScript", "InvalidSkill2", "React"]
        valid = mapper.filter_valid_skills(skills)
        
        assert len(valid) == 3
        assert "Python Programming" in valid
        assert "JavaScript" in valid
        assert "React.js" in valid
    
    def test_get_skill_category(self, mapper):
        """Test getting skill category"""
        category = mapper.get_skill_category("Python")
        assert category == "Programming Languages"
        
        category = mapper.get_skill_category("Machine Learning")
        assert category == "Technical Skills"
    
    def test_statistics(self, mapper):
        """Test getting mapper statistics"""
        stats = mapper.get_statistics()
        assert stats['total_skills'] == 5
        assert 'Programming Languages' in stats['categories']
        assert stats['categories']['Programming Languages'] == 2


class TestSkillValidator:
    """Test SkillValidator functionality"""
    
    def test_validate_skills_names_only(self, validator):
        """Test validating skills returns names"""
        skills = ["Python", "JavaScript", "InvalidSkill", "React"]
        validated = validator.validate_skills(skills)
        
        assert len(validated) == 3
        assert "Python Programming" in validated
        assert "JavaScript" in validated
        assert "React.js" in validated
    
    def test_validate_skills_with_mappings(self, validator):
        """Test validating skills returns full mappings"""
        skills = ["Python", "JavaScript"]
        mappings = validator.validate_skills(skills, return_mappings=True)
        
        assert len(mappings) == 2
        assert mappings[0]['esco_skill'] == "Python Programming"
        assert 'confidence' in mappings[0]
        assert 'category' in mappings[0]
    
    def test_validate_resume_skills_list(self, validator):
        """Test validating skills in resume with list structure"""
        resume = {
            "name": "Test Resume",
            "skills": ["Python", "JavaScript", "InvalidSkill", "React"]
        }
        
        result = validator.validate_resume_skills(resume)
        
        assert 'validated_skills' in result
        assert len(result['validated_skills']['all_skills']) == 3
        assert 'by_category' in result['validated_skills']
        assert 'Programming Languages' in result['validated_skills']['by_category']
    
    def test_validate_resume_skills_nested(self, validator):
        """Test validating skills in nested resume structure"""
        resume = {
            "name": "Test Resume",
            "skills": {
                "all_skills": ["Python", "JS", "Machine Learning"],
                "by_category": {}
            }
        }
        
        result = validator.validate_resume_skills(resume)
        
        assert len(result['validated_skills']['all_skills']) == 3
        assert 'validation_metadata' in result['validated_skills']
        assert result['validated_skills']['validation_metadata']['original_count'] == 3
    
    def test_validation_metadata(self, validator):
        """Test validation metadata is included"""
        resume = {
            "skills": ["Python", "InvalidSkill1", "JavaScript", "InvalidSkill2"]
        }
        
        result = validator.validate_resume_skills(resume)
        metadata = result['validated_skills']['validation_metadata']
        
        assert metadata['original_count'] == 4
        assert metadata['validated_count'] == 2
        assert 'threshold' in metadata
        assert len(metadata['mappings']) == 2


class TestIntegration:
    """Integration tests"""
    
    def test_end_to_end_validation(self, mapper, validator):
        """Test complete validation pipeline"""
        # Simulated extracted skills (with noise)
        raw_skills = [
            "Python",
            "JavaScript", 
            "React",
            "InvalidSkill",
            "ML",  # Alias
            "SQL",
            "Pythoon",  # Typo
            "FakeSkill"
        ]
        
        # Validate
        validated = validator.validate_skills(raw_skills, threshold=0.75)
        
        # Should filter out invalid and standardize names
        assert len(validated) >= 5  # At least 5 valid
        assert "Python Programming" in validated
        assert "JavaScript" in validated
        assert "React.js" in validated
        assert "Machine Learning" in validated  # ML mapped
        assert "SQL" in validated
        
        # Invalid skills filtered out
        assert "InvalidSkill" not in validated
        assert "FakeSkill" not in validated
    
    def test_confidence_thresholds(self, mapper):
        """Test different confidence thresholds"""
        # Low threshold - accept fuzzy matches
        result_low = mapper.map_skill("Pthon", threshold=0.6)
        assert result_low is not None
        
        # High threshold - reject poor matches
        result_high = mapper.map_skill("Pthon", threshold=0.95)
        assert result_high is None


def test_real_esco_file_if_exists():
    """Test with real ESCO file if available"""
    real_esco_path = Path("data/skills/validated_skills.json")
    
    if real_esco_path.exists():
        mapper = ESCOSkillMapper(str(real_esco_path))
        
        # Test with real skills
        assert mapper.is_valid_skill("Python")
        assert mapper.is_valid_skill("JavaScript")
        
        # Get statistics
        stats = mapper.get_statistics()
        print(f"\n✅ Real ESCO file loaded:")
        print(f"   Total skills: {stats['total_skills']}")
        print(f"   Categories: {len(stats['categories'])}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
