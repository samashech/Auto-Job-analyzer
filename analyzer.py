import re
from collections import Counter

# Our master list of skills to look for
KNOWN_SKILLS = {"python", "django", "flask", "fastapi", "aws", "docker", "sql", "react", "kubernetes", "git", "linux", "pandas"}

def extract_skills(job_descriptions: list) -> Counter:
    """Extracts and counts skills from a list of job descriptions."""
    skill_counts = Counter()
    
    for job in job_descriptions:
        # Lowercase and remove all non-alphanumeric characters
        clean_text = re.sub(r'[^a-zA-Z0-9\s]', ' ', job["description"].lower())
        words = clean_text.split()
        
        # Find intersection of words in the job description and our known skills
        found_skills = set(words).intersection(KNOWN_SKILLS)
        skill_counts.update(found_skills)
            
    return skill_counts

def calculate_match_score(required_skills: Counter, my_skills: list) -> float:
    """Calculates a percentage match between top job requirements and your profile."""
    # Let's say we only care about matching against the top 5 most requested skills
    top_requirements = [skill for skill, count in required_skills.most_common(5)]
    
    if not top_requirements:
        return 0.0
        
    matches = set(top_requirements).intersection(set(my_skills))
    score = (len(matches) / len(top_requirements)) * 100
    return round(score, 2)
