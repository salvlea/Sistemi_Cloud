class RankingEngine:
    """
    Engine to calculate candidate ranking scores based on job requirements.
    """
    
    def __init__(self):
        # Job-specific required skills
        self.job_requirements = {
            'Software Engineer': {
                'skills': ['python', 'java', 'javascript', 'git', 'sql'],
                'min_experience': 2,
                'education_weight': 0.2
            },
            'Cloud Engineer': {
                'skills': ['aws', 'docker', 'kubernetes', 'terraform', 'devops'],
                'min_experience': 3,
                'education_weight': 0.15
            },
            'Data Scientist': {
                'skills': ['python', 'machine learning', 'sql', 'ai'],
                'min_experience': 2,
                'education_weight': 0.25
            },
            'DevOps Engineer': {
                'skills': ['docker', 'kubernetes', 'ci/cd', 'aws', 'git'],
                'min_experience': 3,
                'education_weight': 0.15
            },
            'General': {
                'skills': ['python', 'java', 'javascript'],
                'min_experience': 1,
                'education_weight': 0.2
            }
        }
    
    def calculate_score(self, cv_data, job_position='General'):
        """
        Calculate ranking score for a candidate.
        
        Args:
            cv_data: Parsed CV data dictionary
            job_position: Target job position
            
        Returns:
            Tuple of (score, skills_matched_string)
        """
        # Get job requirements
        requirements = self.job_requirements.get(job_position, self.job_requirements['General'])
        
        # 1. Skills matching (50% weight)
        skills_score = self._calculate_skills_score(cv_data['skills'], requirements['skills'])
        
        # 2. Experience score (30% weight)
        experience_score = self._calculate_experience_score(
            cv_data['experience_years'],
            requirements['min_experience']
        )
        
        # 3. Education score (20% weight - configurable per job)
        education_score = self._calculate_education_score(cv_data['education'])
        education_weight = requirements['education_weight']
        
        # Calculate weighted total
        total_score = (
            skills_score * 0.5 +
            experience_score * (0.5 - education_weight) +
            education_score * education_weight
        ) * 100
        
        # Generate skills matched string
        matched_skills = [s for s in cv_data['skills'] if s.lower() in [r.lower() for r in requirements['skills']]]
        skills_matched = f"{len(matched_skills)}/{len(requirements['skills'])}"
        
        return round(total_score, 2), skills_matched
    
    def _calculate_skills_score(self, candidate_skills, required_skills):
        """Calculate skills matching score (0-1)."""
        if not required_skills:
            return 1.0
        
        candidate_skills_lower = [s.lower() for s in candidate_skills]
        required_skills_lower = [s.lower() for s in required_skills]
        
        matched = sum(1 for skill in required_skills_lower if skill in candidate_skills_lower)
        return matched / len(required_skills)
    
    def _calculate_experience_score(self, years, min_required):
        """Calculate experience score (0-1)."""
        if years >= min_required + 3:
            return 1.0
        elif years >= min_required:
            return 0.7 + (years - min_required) * 0.1
        elif years >= min_required - 1:
            return 0.5
        else:
            return max(0.2, years * 0.1)
    
    def _calculate_education_score(self, education):
        """Calculate education score (0-1)."""
        education_scores = {
            'PhD': 1.0,
            'MBA': 0.95,
            "Master's Degree": 0.9,
            "Bachelor's Degree": 0.7,
            'Diploma': 0.5,
            'Not specified': 0.3
        }
        
        return education_scores.get(education, 0.3)
