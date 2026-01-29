"""
Unit tests for Ranking Engine
"""
import pytest
from utils.ranking_engine import RankingEngine


class TestRankingEngine:
    """Test suite for RankingEngine class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.engine = RankingEngine()
    
    def test_calculate_score_perfect_match(self):
        """Test score calculation for perfect candidate."""
        cv_data = {
            'skills': ['Python', 'Java', 'JavaScript', 'Git', 'SQL'],
            'experience_years': 5,
            'education': "Master's Degree"
        }
        
        score, skills_matched = self.engine.calculate_score(cv_data, 'Software Engineer')
        
        # Perfect match should have high score
        assert score >= 85
        assert skills_matched == "5/5"
    
    def test_calculate_score_partial_match(self):
        """Test score calculation for partial match."""
        cv_data = {
            'skills': ['Python', 'Git'],
            'experience_years': 2,
            'education': "Bachelor's Degree"
        }
        
        score, skills_matched = self.engine.calculate_score(cv_data, 'Software Engineer')
        
        # Partial match should have medium score
        assert 40 <= score <= 70
        assert skills_matched == "2/5"
    
    def test_calculate_score_no_experience(self):
        """Test score calculation for entry-level candidate."""
        cv_data = {
            'skills': ['Python', 'JavaScript', 'Git'],
            'experience_years': 0,
            'education': "Bachelor's Degree"
        }
        
        score, skills_matched = self.engine.calculate_score(cv_data, 'Software Engineer')
        
        # No experience should lower score
        assert score < 60
    
    def test_calculate_score_cloud_engineer(self):
        """Test score calculation for Cloud Engineer position."""
        cv_data = {
            'skills': ['AWS', 'Docker', 'Kubernetes', 'Terraform', 'DevOps'],
            'experience_years': 4,
            'education': "Master's Degree"
        }
        
        score, skills_matched = self.engine.calculate_score(cv_data, 'Cloud Engineer')
        
        assert score >= 80
        assert skills_matched == "5/5"
    
    def test_calculate_score_data_scientist(self):
        """Test score calculation for Data Scientist position."""
        cv_data = {
            'skills': ['Python', 'Machine Learning', 'SQL', 'AI'],
            'experience_years': 3,
            'education': 'PhD'
        }
        
        score, skills_matched = self.engine.calculate_score(cv_data, 'Data Scientist')
        
        # PhD should boost score for Data Scientist
        assert score >= 85
        assert skills_matched == "4/4"
    
    def test_skills_score_calculation(self):
        """Test individual skills score calculation."""
        candidate_skills = ['Python', 'AWS', 'Docker']
        required_skills = ['python', 'java', 'aws', 'docker', 'sql']
        
        score = self.engine._calculate_skills_score(candidate_skills, required_skills)
        
        # 3 out of 5 skills matched
        assert score == 0.6
    
    def test_skills_score_case_insensitive(self):
        """Test skills matching is case-insensitive."""
        candidate_skills = ['python', 'AWS', 'Docker']
        required_skills = ['Python', 'aws', 'docker']
        
        score = self.engine._calculate_skills_score(candidate_skills, required_skills)
        
        # All 3 should match despite different cases
        assert score == 1.0
    
    def test_experience_score_exceeds_requirement(self):
        """Test experience score when exceeding minimum."""
        score = self.engine._calculate_experience_score(years=5, min_required=2)
        
        # 5 years when 2 required should give max score
        assert score == 1.0
    
    def test_experience_score_meets_requirement(self):
        """Test experience score when meeting minimum."""
        score = self.engine._calculate_experience_score(years=3, min_required=3)
        
        # Meeting minimum should give good score
        assert 0.7 <= score <= 0.8
    
    def test_experience_score_below_requirement(self):
        """Test experience score when below minimum."""
        score = self.engine._calculate_experience_score(years=1, min_required=3)
        
        # Below minimum should give lower score
        assert score < 0.5
    
    def test_education_score_phd(self):
        """Test education score for PhD."""
        score = self.engine._calculate_education_score('PhD')
        assert score == 1.0
    
    def test_education_score_masters(self):
        """Test education score for Master's degree."""
        score = self.engine._calculate_education_score("Master's Degree")
        assert score == 0.9
    
    def test_education_score_bachelors(self):
        """Test education score for Bachelor's degree."""
        score = self.engine._calculate_education_score("Bachelor's Degree")
        assert score == 0.7
    
    def test_education_score_unknown(self):
        """Test education score for unknown/unspecified."""
        score = self.engine._calculate_education_score("Not specified")
        assert score == 0.3
    
    def test_general_position_fallback(self):
        """Test fallback to General position for unknown job."""
        cv_data = {
            'skills': ['Python', 'Java'],
            'experience_years': 2,
            'education': "Bachelor's Degree"
        }
        
        score, _ = self.engine.calculate_score(cv_data, 'Unknown Position')
        
        # Should use General requirements
        assert score > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
