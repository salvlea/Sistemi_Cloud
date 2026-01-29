"""
Unit tests for CV Parser
"""
import pytest
from utils.cv_parser import CVParser


class TestCVParser:
    """Test suite for CVParser class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.parser = CVParser()
    
    def test_extract_email(self):
        """Test email extraction from CV text."""
        text = "My email is john.doe@example.com and you can reach me there."
        result = self.parser._extract_email(text)
        assert result == "john.doe@example.com"
    
    def test_extract_email_not_found(self):
        """Test email extraction when no email present."""
        text = "No email in this text"
        result = self.parser._extract_email(text)
        assert result == "N/A"
    
    def test_extract_phone(self):
        """Test phone number extraction."""
        text = "Contact me at +39 333 1234567 for more info"
        result = self.parser._extract_phone(text)
        assert "+39" in result or "333" in result
    
    def test_extract_skills(self):
        """Test skills extraction with keyword matching."""
        text = """
        I have experience with Python, AWS, and Docker.
        Also familiar with JavaScript and SQL databases.
        """
        result = self.parser._extract_skills(text)
        
        assert "Python" in result
        assert "AWS" in result
        assert "Docker" in result
        assert "JavaScript" in result
        assert "SQL" in result
    
    def test_extract_skills_case_insensitive(self):
        """Test skills extraction is case-insensitive."""
        text = "I know python and aws very well"
        result = self.parser._extract_skills(text)
        
        assert "Python" in result
        assert "AWS" in result
    
    def test_extract_experience_years(self):
        """Test experience years extraction."""
        text = """
        Work Experience:
        - Software Engineer at TechCorp (2020-2024)
        - Junior Developer at StartupXYZ (2018-2020)
        """
        result = self.parser._extract_experience(text)
        
        # Should calculate 4 + 2 = 6 years
        assert result >= 5  # Allow some tolerance
    
    def test_extract_experience_present(self):
        """Test experience extraction with 'present' as end date."""
        text = "Senior Engineer at Company (2020-present)"
        result = self.parser._extract_experience(text)
        
        # Should be at least 4 years (2026 - 2020)
        assert result >= 4
    
    def test_extract_education(self):
        """Test education level extraction."""
        text = "Education: Master's Degree in Computer Science from MIT"
        result = self.parser._extract_education(text)
        
        assert "Master" in result or "MBA" in result
    
    def test_extract_education_phd(self):
        """Test PhD detection."""
        text = "PhD in Artificial Intelligence"
        result = self.parser._extract_education(text)
        
        assert "PhD" in result
    
    def test_parse_complete_cv(self):
        """Test parsing a complete CV text."""
        cv_text = """
        CURRICULUM VITAE
        
        Name: John Doe
        Email: john.doe@email.com
        Phone: +39 333 1234567
        
        SKILLS:
        Python, AWS, Docker, JavaScript, SQL, Git
        
        EXPERIENCE:
        Senior Software Engineer at TechCorp (2020-present)
        - Led development of cloud-native applications
        
        Junior Developer at StartupXYZ (2018-2020)
        - Built REST APIs
        
        EDUCATION:
        Master's Degree in Computer Science - MIT
        Bachelor's Degree - University of Rome
        """
        
        result = self.parser._extract_info(cv_text)
        
        # Verify all fields are extracted
        assert "john.doe@email.com" in result['email']
        assert len(result['skills']) > 0
        assert "Python" in result['skills']
        assert result['experience_years'] >= 4
        assert "Master" in result['education']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
