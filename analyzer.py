import PyPDF2
import re
import spacy

# Load the English NLP model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def extract_skills_with_nlp(text):
    """
    Dynamically extracts potential skills using NLP (Noun Chunks & Entities)
    combined with a broad dictionary of known tech terms.
    """
    doc = nlp(text)
    
    # Common tech keywords to ensure we don't miss the basics
    core_tech = {
        "python", "java", "c++", "c#", "javascript", "typescript", "html", "css",
        "react", "angular", "vue", "node.js", "nodejs", "express", "django", "flask",
        "fastapi", "spring", "aws", "azure", "gcp", "docker", "kubernetes", "sql",
        "mysql", "postgresql", "mongodb", "redis", "linux", "git", "machine learning",
        "deep learning", "nlp", "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn",
        "data analysis", "agile", "scrum", "jira", "ci/cd", "jenkins", "github actions",
        "terraform", "ansible", "c", "ruby", "php", "swift", "kotlin", "go", "rust"
    }
    
    extracted_skills = set()
    
    # 1. Dictionary Matching (exact keyword match)
    text_lower = text.lower()
    for skill in core_tech:
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            extracted_skills.add(skill.title() if len(skill) > 3 else skill.upper())
            
    # 2. NLP Noun Chunk Extraction (looks for dynamic terms like 'RESTful APIs')
    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.lower().strip()
        # Filter out generic pronouns/stop words and keep chunks that look like technologies
        if len(chunk_text) > 2 and len(chunk_text.split()) <= 3 and not chunk.root.is_stop:
            # We add it if it contains known tech suffixes/prefixes or is purely recognized as an entity
            if any(tech_word in chunk_text for tech_word in ['api', 'framework', 'database', 'cloud', 'system', 'tool']):
                extracted_skills.add(chunk_text.title())
                
    return list(extracted_skills)

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
    exp_words = ["senior", "lead", "manager", "years experience", "5+", "architect", "director"]
    level = "Experienced" if any(w in text for w in exp_words) else "Fresher"

    # Dynamic NLP Extraction
    found_skills = extract_skills_with_nlp(raw_text)
            
    return {
        "name": name,
        "email": email,
        "phone": phone,
        "level": level, 
        "skills": found_skills if found_skills else ["Developer"]
    }
