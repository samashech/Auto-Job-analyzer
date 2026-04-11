import PyPDF2
import re
import spacy
from spacy.matcher import PhraseMatcher

# Import SkillNER
from skillNer.skill_extractor_class import SkillExtractor
from skillNer.general_params import SKILL_DB

# Load the English NLP model
try:
    nlp = spacy.load("en_core_web_lg")
except OSError:
    import spacy.cli
    print("Downloading en_core_web_lg model (larger, more accurate)...")
    spacy.cli.download("en_core_web_lg")
    nlp = spacy.load("en_core_web_lg")

# Initialize SkillExtractor once at the module level
skill_extractor = SkillExtractor(nlp, SKILL_DB, PhraseMatcher)

# Extended skill patterns for common technical skills that SkillNER might miss
TECHNICAL_SKILL_PATTERNS = {
    # Programming Languages
    "Python", "Java", "JavaScript", "TypeScript", "C", "C++", "C#", "Ruby", "Go", "Golang",
    "Rust", "Kotlin", "Swift", "Scala", "Perl", "PHP", "Dart", "R", "MATLAB", "Haskell",
    
    # Web Technologies
    "HTML", "CSS", "React", "Angular", "Vue", "Vue.js", "Node.js", "Node", "Django", "Flask",
    "FastAPI", "Express", "Spring Boot", "Rails", "Laravel", "jQuery", "Bootstrap", "Tailwind",
    
    # Databases
    "MySQL", "PostgreSQL", "MongoDB", "Redis", "SQLite", "Oracle", "SQL Server", "MariaDB",
    "Cassandra", "DynamoDB", "Elasticsearch",
    
    # Cloud & DevOps
    "AWS", "Azure", "GCP", "Google Cloud", "Docker", "Kubernetes", "Jenkins", "Git", "GitHub",
    "GitLab", "Bitbucket", "Terraform", "Ansible", "Linux", "Unix", "Shell Scripting", "Bash",
    
    # Design Tools
    "Adobe Photoshop", "Photoshop", "Adobe Illustrator", "Illustrator", "Adobe InDesign", "InDesign",
    "Figma", "Canva", "Sketch", "InVision", "After Effects", "Premiere Pro", "Final Cut Pro",
    "Blender", "AutoCAD", "CorelDRAW",
    
    # Frameworks & Libraries
    "TensorFlow", "PyTorch", "Scikit-Learn", "Pandas", "NumPy", "Matplotlib", "Seaborn",
    "OpenCV", "Keras", "React Native", "Flutter", "Electron",
    
    # Methodologies & Concepts
    "Agile", "Scrum", "REST", "GraphQL", "Microservices", "CI/CD", "TDD", "BDD",
    "Object-Oriented Programming", "OOP", "Data Structures", "Algorithms", "Machine Learning",
    "Deep Learning", "NLP", "Computer Vision",
    
    # Operating Systems
    "Linux", "Windows", "MacOS", "Ubuntu", "CentOS", "Red Hat", "Debian",
    
    # Other Common Skills
    "API Development", "Database Design", "System Architecture", "Problem Solving",
    "Project Management", "Team Leadership", "Communication", "Critical Thinking"
}


def extract_skills_with_regex(text):
    """
    Fallback skill extraction using regex patterns.
    Catches skills that SkillNER might miss.
    """
    found_skills = set()
    text_lower = text.lower()
    
    for skill in TECHNICAL_SKILL_PATTERNS:
        # Search for skill name (case-insensitive)
        skill_lower = skill.lower()
        if skill_lower in text_lower:
            found_skills.add(skill.title())
    
    return list(found_skills)


def extract_skills_with_nlp(text):
    """
    Dynamically extracts skills using SkillNER, which is backed by the comprehensive ESCO database.
    """
    try:
        # Clean text slightly to improve matching
        clean_text = re.sub(r'[^a-zA-Z0-9\s.,;-]', ' ', text)
        annotations = skill_extractor.annotate(clean_text)

        extracted_skills = set()

        # 1. Full Matches
        for match in annotations.get("results", {}).get("full_matches", []):
            skill_id = match["skill_id"]
            skill_name = SKILL_DB[skill_id]["skill_name"]
            # Formatting to Capitalize Every Word
            extracted_skills.add(skill_name.title())

        # 2. N-gram Matches (lowered threshold to catch more skills)
        for match in annotations.get("results", {}).get("ngram_scored", []):
            skill_id = match["skill_id"]
            if match.get("score", 0) > 0.5:  # Lowered from 0.6 to catch more
                skill_name = SKILL_DB[skill_id]["skill_name"]
                extracted_skills.add(skill_name.title())

        return list(extracted_skills)
    except Exception as e:
        print(f"Skill extraction error: {e}")
        return []


def extract_all_skills(text, raw_text):
    """
    Combines SkillNER extraction with regex-based fallback.
    Ensures maximum skill coverage.
    """
    # Method 1: SkillNER (NLP-based)
    nlp_skills = extract_skills_with_nlp(text)
    
    # Method 2: Regex-based extraction (fallback)
    regex_skills = extract_skills_with_regex(raw_text)
    
    # Combine both methods
    all_skills = list(set(nlp_skills + regex_skills))
    
    # Method 3: Infer related skills
    inferred_skills = infer_related_skills(all_skills)
    
    # Combine all
    final_skills = list(set(all_skills + inferred_skills))
    
    print(f"SkillNER found {len(nlp_skills)} skills")
    print(f"Regex found {len(regex_skills)} skills")
    print(f"Inferred {len(inferred_skills)} related skills")
    print(f"Total unique skills: {len(final_skills)}")
    
    return final_skills


# Skill inference database - if user has skill A, they likely know skill B
SKILL_INFERENCE_MAP = {
    # Web Development
    "Html": ["JavaScript", "CSS", "Web Development", "Responsive Design"],
    "CSS": ["JavaScript", "HTML", "Responsive Design", "Bootstrap"],
    "JavaScript": ["HTML", "CSS", "Web Development", "Node", "React"],
    "React": ["JavaScript", "HTML", "CSS", "Node", "Redux"],
    "Angular": ["JavaScript", "TypeScript", "HTML", "CSS"],
    "Vue": ["JavaScript", "HTML", "CSS", "Vuex"],
    "Node": ["JavaScript", "Express", "MongoDB", "REST"],
    "Node.Js": ["JavaScript", "Express", "MongoDB", "REST"],
    "Django": ["Python", "REST", "PostgreSQL", "HTML"],
    "Flask": ["Python", "REST", "SQLAlchemy"],
    
    # Systems & OS
    "Linux": ["Desktop Systems", "Unix", "Shell Scripting", "Bash", "Ubuntu"],
    "Unix": ["Linux", "Shell Scripting", "Bash"],
    "Windows": ["Desktop Systems", "Microsoft Office", "Active Directory"],
    "Ubuntu": ["Linux", "Desktop Systems"],
    
    # Databases
    "Mysql": ["SQL", "Database Design", "PostgreSQL"],
    "Postgresql": ["SQL", "Database Design", "MySQL"],
    "Mongodb": ["NoSQL", "Database Design", "JavaScript"],
    "Oracle": ["SQL", "Cloud Services", "Database Design"],
    "Sql": ["MySQL", "PostgreSQL", "Database Design"],
    
    # Cloud & DevOps
    "Aws": ["Cloud Services", "Devops", "Linux", "Docker"],
    "Azure": ["Cloud Services", "Devops", "Windows"],
    "Gcp": ["Cloud Services", "Devops", "Linux"],
    "Google Cloud": ["Cloud Services", "Devops", "Linux"],
    "Docker": ["Linux", "Devops", "Cloud Services"],
    "Kubernetes": ["Docker", "Cloud Services", "Devops"],
    "Cloud Services": ["AWS", "Azure", "Devops"],
    
    # Design
    "Adobe Photoshop": ["Adobe Illustrator", "Image Editing", "Graphic Design", "Canva"],
    "Adobe Illustrator": ["Adobe Photoshop", "Graphic Design", "Vector Graphics"],
    "Adobe Indesign": ["Adobe Photoshop", "Graphic Design", "Typography"],
    "Figma": ["UI/UX Design", "Prototyping", "Adobe XD"],
    "Canva": ["Graphic Design", "Social Media Design"],
    "Graphic Design": ["Adobe Photoshop", "Typography", "Color Theory", "Layout Design"],
    "Typography": ["Graphic Design", "Layout Design", "Adobe InDesign"],
    "Color Theory": ["Graphic Design", "Adobe Photoshop"],
    "Sketch": ["UI/UX Design", "Figma", "Prototyping"],
    
    # Fashion & Textile
    "Stitching": ["Draping", "Pattern Making", "Fashion Design", "Textile Design"],
    "Draping": ["Stitching", "Fashion Design", "Pattern Making"],
    "Pattern Making": ["Stitching", "Draping", "Fashion Design"],
    "Fashion Design": ["Stitching", "Draping", "Textile Design", "Adobe Illustrator"],
    "Textile Design": ["Fashion Design", "Stitching"],
    
    # Data Science & ML
    "Python": ["SQL", "Data Analysis", "Git"],
    "Tensorflow": ["Machine Learning", "Python", "Deep Learning"],
    "Pytorch": ["Machine Learning", "Python", "Deep Learning"],
    "Machine Learning": ["Python", "Data Analysis", "Statistics"],
    "Deep Learning": ["Machine Learning", "Python", "Neural Networks"],
    "Pandas": ["Python", "Data Analysis", "NumPy"],
    "Numpy": ["Python", "Data Analysis", "Pandas"],
    
    # Programming Languages
    "Java": ["SQL", "Git", "Object-Oriented Programming"],
    "C++": ["C", "Object-Oriented Programming", "Data Structures"],
    "C#": [".NET", "SQL", "Object-Oriented Programming"],
    "Go": ["Linux", "Cloud Services", "Docker"],
    "Golang": ["Linux", "Cloud Services", "Docker"],
    "Rust": ["Systems Programming", "Linux"],
    "Kotlin": ["Java", "Android Development"],
    "Swift": ["iOS Development", "Xcode"],
    
    # Mobile Development
    "React Native": ["JavaScript", "React", "Mobile Development"],
    "Flutter": ["Dart", "Mobile Development"],
    "Android Development": ["Java", "Kotlin", "Mobile Development"],
    "Ios Development": ["Swift", "Xcode", "Mobile Development"],
    
    # Project Management & Soft Skills
    "Agile": ["Scrum", "Project Management", "Jira"],
    "Scrum": ["Agile", "Project Management"],
    "Project Management": ["Agile", "Team Leadership", "Communication"],
    "Jira": ["Agile", "Scrum", "Project Management"],
    
    # Testing
    "Selenium": ["Automation Testing", "Python", "JavaScript"],
    "Jest": ["JavaScript", "React", "Testing"],
    "Pytest": ["Python", "Testing"],
    
    # API & Backend
    "Rest": ["API Development", "JSON", "Web Services"],
    "Graphql": ["API Development", "JavaScript"],
    "API Development": ["REST", "JSON", "Web Services"],
}


def infer_related_skills(extracted_skills):
    """
    Infers related skills based on extracted skills.
    If user has skill A, they likely know skills in SKILL_INFERENCE_MAP[A].
    """
    inferred = set()
    extracted_lower = {s.lower(): s for s in extracted_skills}
    
    for skill in extracted_skills:
        skill_key = skill.title()
        
        # Check if this skill has related skills in the map
        if skill_key in SKILL_INFERENCE_MAP:
            for related_skill in SKILL_INFERENCE_MAP[skill_key]:
                # Don't add if user already has it
                if related_skill.lower() not in extracted_lower:
                    inferred.add(related_skill)
    
    return list(inferred)

def analyze_resume(pdf_path):
    text = ""
    raw_text = ""
    
    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    raw_text += extracted + "\n"
                    text += extracted.lower() + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")

    # Extract Email
    email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', raw_text)
    email = email_match.group(0) if email_match else ""

    # Extract Phone
    phone_match = re.search(r'\(?\b[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b', raw_text)
    phone = phone_match.group(0) if phone_match else ""

    # Heuristic for Name: First non-empty line
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
    name = lines[0] if lines else "Applicant"
    if len(name) > 30:
        name = "Applicant"

    # Logic for Level Detection
    # Avoid false positives like "Senior Secondary"
    clean_text_for_level = text.replace("senior secondary", "").replace("senior school", "")
    
    exp_words = ["senior", "lead", "manager", "years experience", "5+", "architect", "director", "professional", "specialist"]
    level = "Experienced" if any(w in clean_text_for_level for w in exp_words) else "Fresher"

    # If education is current, likely a fresher
    if "2024" in text or "2025" in text or "2026" in text or "2027" in text:
        if "present" in text or "current" in text:
            level = "Fresher"

    # Combined Skill Extraction (NLP + Regex)
    found_skills = extract_all_skills(text, raw_text)

    # 1. Clean skills for sorting (remove parentheses and descriptive text)
    cleaned_found = []
    for s in found_skills:
        # Remove everything in parentheses: "Python (Programming Language)" -> "Python"
        clean = re.sub(r'\(.*?\)', '', s).strip()
        if len(clean) >= 2 or clean.lower() in ["c++", "c#", "r", "go"]:
            cleaned_found.append(clean)

    # 2. Sort by length ASCENDING (shorter = likely more core tech)
    # Remove duplicates
    cleaned_found = sorted(list(set(cleaned_found)), key=len)

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "level": level,
        "skills": cleaned_found
    }
