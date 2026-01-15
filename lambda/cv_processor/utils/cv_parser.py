import re
import PyPDF2
from io import BytesIO
import docx

class CVParser:
    """
    Utility class to parse CV files (PDF, DOC, DOCX) and extract relevant information.
    """
    
    def __init__(self):
        self.skills_keywords = [
            'python', 'java', 'javascript', 'react', 'node.js', 'aws', 'docker',
            'kubernetes', 'sql', 'mongodb', 'machine learning', 'ai', 'git',
            'agile', 'scrum', 'html', 'css', 'typescript', 'go', 'rust',
            'cloud', 'devops', 'ci/cd', 'terraform', 'ansible'
        ]
    
    def parse(self, file_content, filename):
        """
        Parse CV file and extract structured information.
        
        Args:
            file_content: Binary content of the CV file
            filename: Name of the file
            
        Returns:
            Dictionary with parsed CV data
        """
        # Determine file type and extract text
        if filename.lower().endswith('.pdf'):
            text = self._parse_pdf(file_content)
        elif filename.lower().endswith('.docx'):
            text = self._parse_docx(file_content)
        elif filename.lower().endswith('.doc'):
            # For .doc files, use simplified extraction (requires additional libraries)
            text = self._parse_text_fallback(file_content)
        else:
            text = str(file_content, 'utf-8', errors='ignore')
        
        # Extract structured information
        return {
            'name': self._extract_name(text),
            'email': self._extract_email(text),
            'phone': self._extract_phone(text),
            'skills': self._extract_skills(text),
            'experience_years': self._extract_experience_years(text),
            'education': self._extract_education(text),
            'raw_text': text
        }
    
    def _parse_pdf(self, content):
        """Extract text from PDF file."""
        try:
            pdf_file = BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ''
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            print(f"Error parsing PDF: {str(e)}")
            return ""
    
    def _parse_docx(self, content):
        """Extract text from DOCX file."""
        try:
            doc_file = BytesIO(content)
            doc = docx.Document(doc_file)
            text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            print(f"Error parsing DOCX: {str(e)}")
            return ""
    
    def _parse_text_fallback(self, content):
        """Fallback text extraction."""
        try:
            return str(content, 'utf-8', errors='ignore')
        except:
            return ""
    
    def _extract_name(self, text):
        """Extract candidate name (simple heuristic: first line or first capitalized words)."""
        lines = text.strip().split('\n')
        for line in lines[:5]:  # Check first 5 lines
            clean_line = line.strip()
            if clean_line and len(clean_line.split()) <= 4:
                # Likely a name if it's short and capitalized
                if clean_line[0].isupper():
                    return clean_line
        return "Unknown Candidate"
    
    def _extract_email(self, text):
        """Extract email address using regex."""
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(pattern, text)
        return match.group(0) if match else None
    
    def _extract_phone(self, text):
        """Extract phone number using regex."""
        pattern = r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]'
        match = re.search(pattern, text)
        return match.group(0).strip() if match else None
    
    def _extract_skills(self, text):
        """Extract skills by matching against keyword list."""
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.skills_keywords:
            if skill.lower() in text_lower:
                found_skills.append(skill.title())
        
        return found_skills
    
    def _extract_experience_years(self, text):
        """Estimate years of experience based on date patterns."""
        # Look for year ranges like "2018-2023" or "2018 - present"
        pattern = r'(19|20)\d{2}\s*[-–]\s*(present|current|(19|20)\d{2})'
        matches = re.findall(pattern, text.lower())
        
        if not matches:
            return 0
        
        # Calculate total years (simplified)
        current_year = 2026
        total_years = 0
        
        for match in matches:
            start = int(match[0] + match[1])
            if 'present' in match[2] or 'current' in match[2]:
                end = current_year
            else:
                end = int(match[2][-4:])
            total_years += max(0, end - start)
        
        return min(total_years, 40)  # Cap at 40 years
    
    def _extract_education(self, text):
        """Extract highest education level."""
        text_lower = text.lower()
        
        education_levels = [
            ('phd', 'PhD'),
            ('doctorate', 'PhD'),
            ('master', "Master's Degree"),
            ('msc', "Master's Degree"),
            ('mba', 'MBA'),
            ('bachelor', "Bachelor's Degree"),
            ('bsc', "Bachelor's Degree"),
            ('diploma', 'Diploma')
        ]
        
        for keyword, level in education_levels:
            if keyword in text_lower:
                return level
        
        return 'Not specified'
