import re

ROLE_INFERENCE_MAP = {
    "Frontend Developer": ["React", "Angular", "Vue", "HTML", "CSS", "JavaScript", "TypeScript", "Tailwind", "Next.js"],
    "Backend Developer": ["Node.js", "Django", "Flask", "Spring Boot", "Express", "Java", "Python", "Go", "Ruby", "PHP"],
    "Full Stack Developer": ["React", "Node.js", "MongoDB", "Express", "Django", "JavaScript", "Python"],
    "Data Scientist": ["Python", "Machine Learning", "Deep Learning", "Pandas", "NumPy", "Scikit-Learn", "TensorFlow", "PyTorch"],
    "Data Analyst": ["SQL", "Excel", "Tableau", "Power BI", "Python", "Pandas", "Data Visualization"],
    "DevOps Engineer": ["AWS", "Docker", "Kubernetes", "Jenkins", "Linux", "Terraform", "CI/CD", "Ansible"],
    "Cloud Engineer": ["AWS", "Azure", "GCP", "Google Cloud", "Cloud Computing"],
    "Mobile Developer": ["React Native", "Flutter", "Swift", "Kotlin", "Android", "iOS"],
    "UI/UX Designer": ["Figma", "Adobe XD", "Sketch", "Wireframing", "Prototyping", "User Research"],
    "Graphic Designer": ["Adobe Photoshop", "Adobe Illustrator", "Canva", "Graphic Design"],
    "Database Administrator": ["SQL", "MySQL", "PostgreSQL", "Oracle", "MongoDB", "Database Design"],
    "Security Engineer": ["Cybersecurity", "Penetration Testing", "Network Security", "Cryptography"],
    "Software Engineer": ["Java", "C++", "C#", "Python", "Algorithms", "Data Structures"]
}

def infer_job_role(skills):
    if not skills:
        return "Software Developer"
    
    role_scores = {role: 0 for role in ROLE_INFERENCE_MAP}
    skills_lower = [s.lower() for s in skills]
    
    for role, role_skills in ROLE_INFERENCE_MAP.items():
        for rs in role_skills:
            if rs.lower() in skills_lower:
                role_scores[role] += 1
                
    best_role = max(role_scores, key=role_scores.get)
    if role_scores[best_role] > 0:
        return best_role
    return "Software Developer"
