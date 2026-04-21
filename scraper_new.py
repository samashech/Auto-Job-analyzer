import urllib.parse
import re
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from playwright_stealth import Stealth
import time
import random

# Job type to site mapping - defines which sites to scrape for each job type
JOB_TYPE_SITES = {
    "Full-time": [
        "Naukri", "LinkedIn", "Indeed", "Monster", "FlexJob"
    ],
    "Part-time": [
        "Naukri", "Indeed", "Apna", "Glassdoor", "Snagajob"
    ],
    "Freelance": [
        "Upwork", "Fiverr", "Freelancer", "PeoplePerHour", "Toptal"
    ],
    "Internship": [
        "Internshala", "LinkedIn", "Indeed", "Unstop", "WayUp"
    ]
}

# Top Legitimate Sites Categorized (kept for reference, JOB_TYPE_SITES is authoritative)
LEGIT_SITES = {
    "Full-time": [
        {"name": "LinkedIn", "base": "https://www.linkedin.com/jobs/search/?keywords={query}", "scrape": True},
        {"name": "Indeed", "base": "https://in.indeed.com/jobs?q={query}", "scrape": True},
        {"name": "Glassdoor", "base": "https://www.glassdoor.com/Job/jobs.htm?sc.keyword={query}", "scrape": True},
        {"name": "Wellfound", "base": "https://wellfound.com/role/l/{dash_query}", "scrape": True},
        {"name": "Naukri", "base": "https://www.naukri.com/{dash_query}-jobs", "scrape": True},
        {"name": "ZipRecruiter", "base": "https://www.ziprecruiter.in/jobs/search?q={query}", "scrape": False},
        {"name": "Monster", "base": "https://www.foundit.in/srp/results?query={query}", "scrape": True},
        {"name": "SimplyHired", "base": "https://www.simplyhired.co.in/search?q={query}", "scrape": False},
        {"name": "Dice", "base": "https://www.dice.com/jobs?q={query}", "scrape": True},
        {"name": "CareerBuilder", "base": "https://www.careerbuilder.com/jobs?keywords={query}", "scrape": False}
    ],
    "Part-time": [
        {"name": "LinkedIn Part-Time", "base": "https://www.linkedin.com/jobs/search/?keywords={query}%20Part%20Time", "scrape": True},
        {"name": "Indeed Part-Time", "base": "https://in.indeed.com/jobs?q={query}+part+time", "scrape": True},
        {"name": "FlexJobs", "base": "https://www.flexjobs.com/search?search={query}&schedule=Part-Time", "scrape": False},
        {"name": "Glassdoor Part-Time", "base": "https://www.glassdoor.com/Job/jobs.htm?sc.keyword={query}%20part+time", "scrape": True},
        {"name": "Snagajob", "base": "https://www.snagajob.com/search?q={query}", "scrape": False},
        {"name": "SimplyHired", "base": "https://www.simplyhired.co.in/search?q={query}+part+time", "scrape": False},
        {"name": "ZipRecruiter", "base": "https://www.ziprecruiter.in/jobs/search?q={query}+part+time", "scrape": False},
        {"name": "Wellfound", "base": "https://wellfound.com/role/l/{dash_query}-part-time", "scrape": True},
        {"name": "Upwork", "base": "https://www.upwork.com/nx/search/jobs/?q={query}", "scrape": True},
        {"name": "Fiverr", "base": "https://www.fiverr.com/search/gigs?query={query}", "scrape": False}
    ],
    "Internship": [
        {"name": "Internshala", "base": "https://internshala.com/internships/keywords-{dash_query}/", "scrape": True},
        {"name": "LinkedIn Internships", "base": "https://www.linkedin.com/jobs/search/?keywords={query}%20Internship", "scrape": True},
        {"name": "WayUp", "base": "https://www.wayup.com/s/internships/{dash_query}/", "scrape": False},
        {"name": "Glassdoor Interns", "base": "https://www.glassdoor.com/Job/jobs.htm?sc.keyword={query}%20internship", "scrape": True},
        {"name": "Indeed Interns", "base": "https://in.indeed.com/jobs?q={query}+internship", "scrape": True},
        {"name": "Chegg Internships", "base": "https://www.internships.com/search?q={query}", "scrape": False},
        {"name": "Handshake", "base": "https://app.joinhandshake.com/stu/postings?query={query}", "scrape": False},
        {"name": "LetsIntern", "base": "https://www.letsintern.com/internships?q={query}", "scrape": True},
        {"name": "Wellfound Interns", "base": "https://wellfound.com/role/l/{dash_query}-internship", "scrape": True},
        {"name": "Naukri Interns", "base": "https://www.naukri.com/{dash_query}-internship-jobs", "scrape": True},
        {"name": "TimesJobs Interns", "base": "https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords={timesjobs_query}&txtLocation=", "scrape": True}
    ],
    "Freelance": [
        {"name": "Upwork", "base": "https://www.upwork.com/nx/search/jobs/?q={query}", "scrape": True},
        {"name": "Freelancer", "base": "https://www.freelancer.com/jobs/?keyword={query}", "scrape": True},
        {"name": "Fiverr", "base": "https://www.fiverr.com/search/gigs?query={query}", "scrape": False},
        {"name": "Toptal", "base": "https://www.toptal.com/talent/apply", "scrape": False},
        {"name": "Guru", "base": "https://www.guru.com/d/jobs/q/{query}/", "scrape": False},
        {"name": "PeoplePerHour", "base": "https://www.peopleperhour.com/freelance-jobs?q={query}", "scrape": True},
        {"name": "FlexJobs", "base": "https://www.flexjobs.com/search?search={query}&jobType=Freelance", "scrape": False},
        {"name": "SolidGigs", "base": "https://solidgigs.com/", "scrape": False},
        {"name": "WeWorkRemotely", "base": "https://weworkremotely.com/remote-jobs/search?term={query}", "scrape": True},
        {"name": "Hubstaff Talent", "base": "https://talent.hubstaff.com/search/jobs?search={query}", "scrape": False}
    ]
}


def clean_skill_for_search(skill):
    """
    Cleans up SkillNER's descriptive skill names for search queries.
    Removes parentheses, handles special characters, etc.
    """
    skill = re.sub(r'\(.*?\)', '', skill).strip()
    replacements = {
        "Cascading Style Sheets": "CSS",
        "Hypertext Markup Language": "HTML",
        "Gcp": "Google Cloud",
        "Aws": "AWS",
        "Scikit-Learn": "Scikit Learn"
    }
    for old, new in replacements.items():
        if old in skill:
            skill = skill.replace(old, new)
    return skill


def normalize_url(url):
    """
    Normalizes a job URL by removing common tracking and session parameters.
    Ensures that identical jobs with different tracking IDs are treated as one.
    """
    if not url or url == '#' or not url.startswith('http'):
        return url
    try:
        parsed = urllib.parse.urlparse(url)
        query = urllib.parse.parse_qs(parsed.query)
        
        # Tracking/Session parameters to remove
        junk_params = [
            'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
            'src', 'sid', 'sp', 'ref', 'click_id', 'aff_id', 'tracking',
            'jobsearchDesk', 'searchId', 'applySrc', 'sid', 'clickid', 'gl',
            'source', 'f', 'itid', 'job_role', 'experience', 'location',
            'q', 'search_query', 'search_id', 'pos', 'page', 'tmp', 'total_count'
        ]
        
        for p in junk_params:
            query.pop(p, None)
            
        new_query = urllib.parse.urlencode(query, doseq=True)
        path = parsed.path.rstrip('/')
        
        return urllib.parse.urlunparse(parsed._replace(path=path, query=new_query, fragment=''))
    except:
        return url


# Job role mapping for sites that need specific job titles (Glassdoor, etc.)
GLASSDOOR_ROLE_EXPANSIONS = {
    # OS & Infrastructure
    "Linux": ["Linux Administrator", "Linux Engineer", "Linux System Administrator", "Linux DevOps"],
    "Unix": ["Unix Administrator", "Unix Engineer", "Unix Systems Administrator"],
    "Windows": ["Windows Administrator", "Windows Engineer", "Desktop Support"],
    "Ubuntu": ["Ubuntu Administrator", "Linux Administrator", "Cloud Engineer"],
    
    # Programming Languages
    "Python": ["Python Developer", "Python Engineer", "Software Engineer Python"],
    "Java": ["Java Developer", "Java Engineer", "Software Engineer Java"],
    "JavaScript": ["JavaScript Developer", "JavaScript Engineer", "Frontend Developer"],
    "C++": ["C++ Developer", "C++ Engineer", "Software Engineer C++"],
    "C#": ["C# Developer", "C# Engineer", ".NET Developer"],
    
    # Web Technologies
    "Html": ["Frontend Developer", "Web Developer", "UI Developer"],
    "Css": ["Frontend Developer", "Web Developer", "UI Developer"],
    "React": ["React Developer", "React Engineer", "Frontend Engineer React"],
    "Angular": ["Angular Developer", "Angular Engineer", "Frontend Engineer"],
    "Node": ["Node Developer", "Node Engineer", "Backend Engineer"],
    "Node.Js": ["Node.js Developer", "Node.js Engineer", "Backend Engineer"],
    "Django": ["Django Developer", "Django Engineer", "Python Backend Developer"],
    
    # Cloud & DevOps
    "Aws": ["AWS Engineer", "Cloud Engineer AWS", "AWS Architect"],
    "Azure": ["Azure Engineer", "Cloud Engineer Azure", "Azure Architect"],
    "Google Cloud": ["GCP Engineer", "Cloud Engineer GCP", "Google Cloud Architect"],
    "Docker": ["DevOps Engineer", "Docker Engineer", "Container Engineer"],
    "Kubernetes": ["DevOps Engineer", "Kubernetes Engineer", "Platform Engineer"],
    "Devops": ["DevOps Engineer", "Site Reliability Engineer", "Infrastructure Engineer"],
    
    # Databases
    "Mysql": ["Database Developer", "MySQL Developer", "Database Administrator"],
    "Postgresql": ["Database Developer", "PostgreSQL Developer", "Database Administrator"],
    "Mongodb": ["Database Developer", "MongoDB Developer", "NoSQL Developer"],
    "Oracle": ["Oracle Developer", "Oracle DBA", "Database Administrator Oracle"],
    
    # Data & ML
    "Machine Learning": ["Machine Learning Engineer", "ML Engineer", "AI Engineer"],
    "Deep Learning": ["Deep Learning Engineer", "AI Researcher", "ML Engineer"],
    "Tensorflow": ["ML Engineer", "AI Engineer", "Deep Learning Engineer"],
    "Pytorch": ["ML Engineer", "AI Engineer", "Research Engineer"],
    "Python": ["Data Scientist", "Data Analyst", "ML Engineer"],
    
    # Design
    "Adobe Photoshop": ["Graphic Designer", "Visual Designer", "UI Designer"],
    "Adobe Illustrator": ["Graphic Designer", "Visual Designer", "Brand Designer"],
    "Figma": ["UI Designer", "UX Designer", "Product Designer"],
    "Canva": ["Social Media Manager", "Content Creator", "Marketing Designer"],
    "Graphic Design": ["Graphic Designer", "Visual Designer", "Creative Designer"],
    
    # Mobile
    "React Native": ["React Native Developer", "Mobile Engineer", "Cross-Platform Developer"],
    "Flutter": ["Flutter Developer", "Mobile Engineer", "Dart Developer"],
    "Android Development": ["Android Developer", "Android Engineer", "Mobile Developer"],
    "Ios Development": ["iOS Developer", "iOS Engineer", "Mobile Developer"],
    
    # General
    "Sql": ["Database Developer", "SQL Developer", "Data Analyst"],
    "Git": ["Software Engineer", "Developer", "DevOps Engineer"],
    "Rest": ["Backend Developer", "API Developer", "Integration Engineer"],
    "Api Development": ["Backend Developer", "API Developer", "Integration Engineer"],
}

# Wellfound (AngelList) role mapping - startup-focused job titles
WELLFOUND_ROLE_MAP = {
    # Frontend Engineering
    "Html": "Frontend Engineer",
    "Css": "Frontend Engineer",
    "JavaScript": "Frontend Engineer",
    "React": "Frontend Engineer",
    "Angular": "Frontend Engineer",
    "Vue": "Frontend Engineer",
    "Bootstrap": "Frontend Engineer",
    "Tailwind": "Frontend Engineer",
    "Jquery": "Frontend Engineer",
    
    # Backend Engineering
    "Python": "Backend Engineer",
    "Django": "Backend Engineer",
    "Flask": "Backend Engineer",
    "Fastapi": "Backend Engineer",
    "Java": "Backend Engineer",
    "Node": "Backend Engineer",
    "Node.Js": "Backend Engineer",
    "Go": "Backend Engineer",
    "Golang": "Backend Engineer",
    "Ruby": "Backend Engineer",
    "Php": "Backend Engineer",
    "Spring Boot": "Backend Engineer",
    "Rails": "Backend Engineer",
    "Laravel": "Backend Engineer",
    
    # Full Stack (overrides for skills that indicate full-stack)
    "React Native": "Full Stack Engineer",
    
    # Data & ML Engineering
    "Machine Learning": "Machine Learning Engineer",
    "Deep Learning": "Machine Learning Engineer",
    "Tensorflow": "Machine Learning Engineer",
    "Pytorch": "Machine Learning Engineer",
    "Pandas": "Data Engineer",
    "Numpy": "Data Engineer",
    "Scikit-Learn": "Machine Learning Engineer",
    "R": "Data Scientist",
    "Matlab": "Data Scientist",
    
    # DevOps & Cloud
    "Aws": "DevOps Engineer",
    "Azure": "DevOps Engineer",
    "Google Cloud": "DevOps Engineer",
    "Docker": "DevOps Engineer",
    "Kubernetes": "DevOps Engineer",
    "Linux": "DevOps Engineer",
    "Terraform": "DevOps Engineer",
    "Ansible": "DevOps Engineer",
    
    # Mobile Engineering
    "Flutter": "Mobile Engineer",
    "Android Development": "Mobile Engineer",
    "Ios Development": "Mobile Engineer",
    "Swift": "Mobile Engineer",
    "Kotlin": "Mobile Engineer",
    
    # Database
    "Mysql": "Database Engineer",
    "Postgresql": "Database Engineer",
    "Mongodb": "Database Engineer",
    "Redis": "Database Engineer",
    "Oracle": "Database Engineer",
    "Sql": "Database Engineer",
    
    # Design
    "Figma": "Product Designer",
    "Adobe Photoshop": "Product Designer",
    "Adobe Illustrator": "Product Designer",
    "Sketch": "Product Designer",
    "Canva": "Product Designer",
    "Adobe Indesign": "Product Designer",
    "Graphic Design": "Product Designer",
    
    # Product & Management
    "Agile": "Product Manager",
    "Scrum": "Product Manager",
    "Jira": "Product Manager",
    "Project Management": "Product Manager",
    
    # Security
    "Cybersecurity": "Security Engineer",
    "Penetration Testing": "Security Engineer",
    "Network Security": "Security Engineer",
}

# Monster (foundit.in) role mapping - traditional corporate job titles
MONSTER_ROLE_MAP = {
    # IT/Software
    "Html": "Software Developer",
    "Css": "Software Developer",
    "JavaScript": "Software Developer",
    "Python": "Software Developer",
    "Java": "Software Developer",
    "C++": "Software Developer",
    "C#": "Software Developer",
    "React": "Software Developer",
    "Angular": "Software Developer",
    "Node": "Software Developer",
    "Node.Js": "Software Developer",
    "Php": "Software Developer",
    "Django": "Software Developer",
    "Flask": "Software Developer",
    
    # System Admin
    "Linux": "System Administrator",
    "Unix": "System Administrator",
    "Windows": "System Administrator",
    "Ubuntu": "System Administrator",
    "Aws": "Cloud Engineer",
    "Azure": "Cloud Engineer",
    "Google Cloud": "Cloud Engineer",
    "Docker": "DevOps Engineer",
    "Kubernetes": "DevOps Engineer",
    
    # Database
    "Mysql": "Database Administrator",
    "Postgresql": "Database Administrator",
    "Mongodb": "Database Administrator",
    "Oracle": "Database Administrator",
    "Sql": "Database Administrator",
    
    # Data/ML
    "Machine Learning": "Data Scientist",
    "Deep Learning": "Data Scientist",
    "Tensorflow": "Data Scientist",
    "Pytorch": "Data Scientist",
    "R": "Data Analyst",
    "Pandas": "Data Analyst",
    
    # Design
    "Adobe Photoshop": "Graphic Designer",
    "Adobe Illustrator": "Graphic Designer",
    "Figma": "UI/UX Designer",
    "Canva": "Graphic Designer",
    "Graphic Design": "Graphic Designer",
    
    # Networking
    "Networking": "Network Engineer",
    "Ccn": "Network Engineer",
    "Cisco": "Network Engineer",
    
    # Testing
    "Selenium": "Test Engineer",
    "Jest": "Test Engineer",
    "Pytest": "Test Engineer",
    
    # Project Management
    "Agile": "Project Manager",
    "Scrum": "Project Manager",
    "Jira": "Project Manager",
    "Project Management": "Project Manager",
    
    # Mobile
    "React Native": "Mobile Developer",
    "Flutter": "Mobile Developer",
    "Android Development": "Mobile Developer",
    "Ios Development": "Mobile Developer",
}


def get_glassdoor_search_queries(skill):
    """
    For Glassdoor: Generate expanded search queries with proper job titles.
    Returns a list of queries to try for a given skill.
    """
    cleaned_skill = clean_skill_for_search(skill)
    skill_title = cleaned_skill.title()
    
    # If we have specific role mappings, use them
    if skill_title in GLASSDOOR_ROLE_EXPANSIONS:
        return GLASSDOOR_ROLE_EXPANSIONS[skill_title]
    
    # Default: just use the cleaned skill name
    return [cleaned_skill]


def get_wellfound_search_role(skill):
    """
    For Wellfound: Map technical skills to proper startup job roles.
    Returns a job role string for searching.
    """
    cleaned_skill = clean_skill_for_search(skill)
    skill_title = cleaned_skill.title()
    
    # Check if we have a mapping for this skill
    if skill_title in WELLFOUND_ROLE_MAP:
        return WELLFOUND_ROLE_MAP[skill_title]
    
    # Default: use the skill name as-is
    return cleaned_skill


def get_linkedin_search_role(skill):
    """
    For LinkedIn: Map skills to professional job titles.
    Returns a job role string for searching.
    """
    cleaned_skill = clean_skill_for_search(skill)
    skill_title = cleaned_skill.title()
    
    # Use Glassdoor mappings (same professional titles)
    if skill_title in GLASSDOOR_ROLE_EXPANSIONS:
        return GLASSDOOR_ROLE_EXPANSIONS[skill_title][0]  # Use first/best match
    
    # Use Wellfound mappings as fallback
    if skill_title in WELLFOUND_ROLE_MAP:
        return WELLFOUND_ROLE_MAP[skill_title]
    
    # Default: use the skill name as-is
    return cleaned_skill


def get_indeed_search_role(skill):
    """
    For Indeed: Map skills to common job titles.
    Returns a job role string for searching.
    """
    cleaned_skill = clean_skill_for_search(skill)
    skill_title = cleaned_skill.title()
    
    # Use Monster mappings (corporate titles work well on Indeed)
    if skill_title in MONSTER_ROLE_MAP:
        return MONSTER_ROLE_MAP[skill_title]
    
    # Use Glassdoor mappings as fallback
    if skill_title in GLASSDOOR_ROLE_EXPANSIONS:
        return GLASSDOOR_ROLE_EXPANSIONS[skill_title][0]
    
    # Default: use the skill name as-is
    return cleaned_skill


def get_naukri_search_role(skill):
    """
    For Naukri: Map skills to Indian corporate job titles.
    Returns a job role string for searching.
    """
    cleaned_skill = clean_skill_for_search(skill)
    skill_title = cleaned_skill.title()
    
    # Naukri uses similar corporate titles to Monster
    if skill_title in MONSTER_ROLE_MAP:
        return MONSTER_ROLE_MAP[skill_title]
    
    # Use Glassdoor mappings as fallback
    if skill_title in GLASSDOOR_ROLE_EXPANSIONS:
        return GLASSDOOR_ROLE_EXPANSIONS[skill_title][0]
    
    # Default: use the skill name as-is
    return cleaned_skill


def get_timesjobs_search_role(skill):
    """
    For TimesJobs: Map skills to job titles.
    Returns a job role string for searching.
    """
    cleaned_skill = clean_skill_for_search(skill)
    skill_title = cleaned_skill.title()
    
    # TimesJobs uses similar titles to Monster/Naukri
    if skill_title in MONSTER_ROLE_MAP:
        return MONSTER_ROLE_MAP[skill_title]
    
    # Use Glassdoor mappings as fallback
    if skill_title in GLASSDOOR_ROLE_EXPANSIONS:
        return GLASSDOOR_ROLE_EXPANSIONS[skill_title][0]
    
    # Default: use the skill name as-is
    return cleaned_skill


def get_internshala_search_role(skill, job_type="Full-time"):
    """
    For Internshala: Map skills to internship roles.
    Returns a job role string for searching.
    """
    cleaned_skill = clean_skill_for_search(skill)
    skill_title = cleaned_skill.title()
    
    # Internship-specific mappings (add "Intern" suffix for some roles)
    internship_mappings = {
        "Html": "Web Development",
        "Css": "Web Development",
        "JavaScript": "Web Development",
        "React": "Web Development",
        "Python": "Software Development",
        "Java": "Software Development",
        "Machine Learning": "Data Science",
        "Deep Learning": "Data Science",
        "Aws": "Cloud Computing",
        "Docker": "DevOps",
        "Linux": "System Administration",
        "Adobe Photoshop": "Graphic Design",
        "Figma": "UI/UX Design",
        "Content Writing": "Content Writing",
        "Marketing": "Marketing",
    }
    
    if skill_title in internship_mappings:
        return internship_mappings[skill_title]
    
    # Use Wellfound mappings as fallback
    if skill_title in WELLFOUND_ROLE_MAP:
        return WELLFOUND_ROLE_MAP[skill_title]
    
    # Default: use the skill name as-is
    return cleaned_skill


def get_upwork_search_role(skill):
    """
    For Upwork: Map skills to freelance job titles.
    Returns a job role string for searching.
    """
    cleaned_skill = clean_skill_for_search(skill)
    skill_title = cleaned_skill.title()
    
    # Freelance-specific mappings (use "Developer" instead of "Engineer")
    freelance_mappings = {
        "Html": "Web Developer",
        "Css": "Web Developer",
        "JavaScript": "Web Developer",
        "React": "React Developer",
        "Python": "Python Developer",
        "Java": "Java Developer",
        "Php": "PHP Developer",
        "Wordpress": "WordPress Developer",
        "Shopify": "Shopify Developer",
        "Machine Learning": "ML Engineer",
        "Aws": "Cloud Architect",
        "Docker": "DevOps Engineer",
        "Adobe Photoshop": "Graphic Designer",
        "Figma": "UI/UX Designer",
        "Content Writing": "Content Writer",
        "Video Editing": "Video Editor",
    }
    
    if skill_title in freelance_mappings:
        return freelance_mappings[skill_title]
    
    # Use Glassdoor mappings as fallback
    if skill_title in GLASSDOOR_ROLE_EXPANSIONS:
        return GLASSDOOR_ROLE_EXPANSIONS[skill_title][0]
    
    # Default: use the skill name as-is
    return cleaned_skill


def get_monster_search_role(skill):
    """
    For Monster (foundit.in): Map skills to traditional corporate job titles.
    Returns a job role string for searching.
    """
    cleaned_skill = clean_skill_for_search(skill)
    skill_title = cleaned_skill.title()
    
    # Check if we have a mapping for this skill
    if skill_title in MONSTER_ROLE_MAP:
        return MONSTER_ROLE_MAP[skill_title]
    
    # Default: use the skill name as-is
    return cleaned_skill


def calculate_relevance_score(job_title, job_description, skills):
    """
    Calculates a relevance score (0-100) based on how many user skills
    are mentioned in the job title and description.
    STRICT: Only scores high if actual technical skills are found.
    """
    text_to_check = f"{job_title} {job_description}".lower()
    
    if not skills:
        return 10  # Base score if no specific skills

    skill_lower = [s.lower() for s in skills if len(s) > 2]

    if not skill_lower:
        return 10

    matches = 0
    matched_skills = []
    
    for skill in skill_lower:
        # Full skill match in title or description
        if skill.lower() in text_to_check:
            matches += 1
            matched_skills.append(skill)
        else:
            # Check for partial word matches (e.g., "Python" in "Python Developer")
            skill_words = skill.lower().split()
            for word in skill_words:
                if len(word) > 3 and word in text_to_check:
                    matches += 0.5
                    matched_skills.append(f"{skill}(partial)")
                    break

    # Calculate score based on percentage of skills matched
    match_percentage = matches / len(skill_lower)
    
    # Bonus points if skills appear in title (more relevant)
    title_bonus = 0
    job_title_lower = job_title.lower()
    for skill in skill_lower:
        if skill.lower() in job_title_lower:
            title_bonus += 10

    # Final score: base percentage + title bonus, capped at 100
    score = min(100, int((match_percentage * 80) + title_bonus))
    
    # Return a low non-zero score if there is any text, to avoid filtering out all jobs
    if matches == 0:
        return 5
    
    return score


def _is_blocked(content):
    """Check if the page content indicates blocking/CAPTCHA."""
    if not content:
        return True
    content_lower = content.lower()
    block_indicators = [
        "access denied",
        "captcha",
        "verify you are human",
        "forbidden",
        "403",
        "challenge-platform",
        "suspicious traffic",
        "security check"
    ]
    return any(indicator in content_lower for indicator in block_indicators)


def _create_fallback_job(site_name, job_role, search_url, relevance_score=40, description=""):
    """Create a fallback search link job when scraping fails."""
    return {
        "name": site_name,
        "title": f"{job_role} Jobs on {site_name}",
        "company": "Click to Browse All Jobs",
        "url": search_url,
        "description": description or f"{site_name} has anti-bot protection. Click to browse {job_role} opportunities directly on {site_name}",
        "source": f"{site_name} (Search Link)",
        "relevance_score": relevance_score
    }


def scrape_linkedin(query, skills, experience_level="", location="", page_num=1):
    """Scrape actual job listings from LinkedIn."""
    results = []
    try:
        # Map skill to professional job title
        job_role = get_linkedin_search_role(query)
        
        # Build search query with experience and location
        search_parts = [job_role]
        if location:
            search_parts.append(location)
        if experience_level and 'intern' not in experience_level.lower():
            if 'senior' in experience_level.lower() or 'lead' in experience_level.lower():
                search_parts.append('Senior')
            elif 'entry' in experience_level.lower():
                search_parts.append('Entry Level')
        
        search_query = ' '.join(search_parts)
        encoded_query = urllib.parse.quote(search_query)
        url = f"https://www.linkedin.com/jobs/search/?keywords={encoded_query}"
        print(f"    [LinkedIn] Mapped '{query}' -> '{search_query}', navigating to: {url}")
        
          # Wait for JS to render

        # Check if blocked
        html_content = fetch_html(url, render=True, premium=True)
        if _is_blocked(html_content):
            print(f"    [LinkedIn] Blocked by CAPTCHA, returning search link")
            return [_create_fallback_job("LinkedIn", job_role, url, 45)]

        if 'html_content' not in locals():
            html_content = fetch_html(url, render=True, premium=True)
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Try multiple selectors for LinkedIn's dynamic structure
        job_cards = soup.find_all('div', class_=re.compile(r'base-search-card'))
        
        if not job_cards:
            job_cards = soup.find_all('li', class_=re.compile(r'jobs-search'))
        
        if not job_cards:
            # Fallback: find all job links
            job_cards = soup.find_all('a', href=re.compile(r'/jobs/view/'))
            print(f"    [LinkedIn] Found {len(job_cards)} jobs with fallback selector")
        else:
            print(f"    [LinkedIn] Found {len(job_cards)} jobs")

        for card in job_cards[:8]:
            try:
                # Try to extract job info
                title_elem = card.find('h3', class_=re.compile(r'base-search-card'))
                if not title_elem:
                    title_elem = card.find('a', href=re.compile(r'/jobs/view/'))
                
                if not title_elem:
                    continue

                title = title_elem.text.strip()
                if not title:
                    link_elem = card.find('a', href=re.compile(r'/jobs/view/'))
                    if link_elem:
                        link = link_elem.get('href', '')
                        title = link_elem.text.strip()
                    else:
                        continue
                else:
                    link_elem = card.find('a', href=re.compile(r'/jobs/view/'))
                    link = link_elem.get('href', '') if link_elem else ''

                if not link.startswith('http'):
                    link = f"https://www.linkedin.com{link}" if link else ""

                company_elem = card.find('a', class_=re.compile(r'hidden-nested-link'))
                company = company_elem.text.strip() if company_elem else "LinkedIn Company"

                desc_elem = card.find('div', class_=re.compile(r'job-card-container'))
                description = desc_elem.text.strip()[:300] if desc_elem else f"Job matching: {query}"

                relevance = calculate_relevance_score(title, description, skills)
                if relevance > 0:
                    results.append({
                        "name": "LinkedIn",
                        "title": title,
                        "company": company,
                        "url": link,
                        "description": description,
                        "source": "LinkedIn",
                        "relevance_score": relevance
                    })
            except Exception as e:
                continue
                
        print(f"    [LinkedIn] Extracted {len(results)} relevant jobs")
        
        # If no jobs scraped, return fallback
        if not results:
            print(f"    [LinkedIn] No jobs scraped, returning search link")
            results.append(_create_fallback_job("LinkedIn", job_role, url, 35))
    except Exception as e:
        print(f"    [LinkedIn] Scraping failed: {e}")
        job_role = get_linkedin_search_role(query)
        url = f"https://www.linkedin.com/jobs/search/?keywords={urllib.parse.quote(job_role)}"
        results.append(_create_fallback_job("LinkedIn", job_role, url, 30, f"LinkedIn scraping failed. Click to search for {job_role} jobs."))

    return results


def scrape_indeed(query, skills, experience_level="", location="", page_num=1):
    """Scrape actual job listings from Indeed."""
    results = []
    try:
        # Map skill to common job title
        job_role = get_indeed_search_role(query)
        
        # Build query with location
        search_query = job_role
        if location:
            search_query += f" {location}"
        
        encoded_query = urllib.parse.quote(search_query)
        url = f"https://in.indeed.com/jobs?q={encoded_query}"
        print(f"    [Indeed] Mapped '{query}' -> '{search_query}', navigating to: {url}")
        
        try:
            pass
        except Exception as nav_e:
            print(f"    [Indeed] Navigation failed: {str(nav_e)[:100]}")
            return [_create_fallback_job("Indeed", job_role, url, 30)]

        if 'html_content' not in locals():
            html_content = fetch_html(url, render=True, premium=True)
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Indeed uses dynamic IDs, use flexible selectors
        job_cards = soup.find_all('div', id=re.compile(r'^p_'))
        
        if not job_cards:
            job_cards = soup.find_all('div', class_=re.compile(r'job_seen'))
        
        if not job_cards:
            job_cards = soup.find_all('a', class_=re.compile(r'jobTitle'))
            print(f"    [Indeed] Found {len(job_cards)} jobs with fallback")
        else:
            print(f"    [Indeed] Found {len(job_cards)} jobs")

        for card in job_cards[:8]:
            try:
                title_elem = card.find('a', class_=re.compile(r'jobTitle'))
                if not title_elem:
                    h2 = card.find('h2')
                    title_elem = h2.find('a') if h2 else None
                
                if not title_elem:
                    continue

                title = title_elem.text.strip()
                link = title_elem.get('href', '')
                if not link.startswith('http'):
                    link = f"https://in.indeed.com{link}" if link else ""

                company_elem = card.find('span', class_=re.compile(r'companyName'))
                company = company_elem.text.strip() if company_elem else "Indeed Employer"

                desc_elem = card.find('div', class_=re.compile(r'job-snippet'))
                description = desc_elem.text.strip()[:300] if desc_elem else f"Job matching: {query}"

                relevance = calculate_relevance_score(title, description, skills)
                if relevance > 0:
                    results.append({
                        "name": "Indeed",
                        "title": title,
                        "company": company,
                        "url": link,
                        "description": description,
                        "source": "Indeed",
                        "relevance_score": relevance
                    })
            except Exception as e:
                continue
                
        print(f"    [Indeed] Extracted {len(results)} relevant jobs")
    except Exception as e:
        print(f"    [Indeed] Scraping failed: {e}")

    return results


def scrape_naukri(query, skills, experience_level="", location="", page_num=1):
    """
    Scrape actual job listings from Naukri.
    NOTE: Naukri has strong anti-bot protection, so we use a hybrid approach:
    1. Try to scrape with advanced stealth
    2. If blocked, return direct search links that work
    """
    results = []
    try:
        # Map skill to Indian corporate job title
        job_role = get_naukri_search_role(query)
        dash_query = job_role.replace(' ', '-')
        
        # Try the new Naukri URL format that's less likely to be blocked
        url = f"https://www.naukri.com/naukri/search/results?keyword={urllib.parse.quote(job_role)}"
        print(f"    [Naukri] Mapped '{query}' -> '{job_role}', navigating to: {url}")
        
        # Try to access with longer wait
        
          # Longer wait for JS
        
        # Check if we got blocked
        if "Access Denied" in page.content() or "nucaptcha" in page.content().lower():
            print(f"    [Naukri] Blocked by anti-bot, returning search link")
            # Return a direct search link instead
            search_url = f"https://www.naukri.com/{dash_query}-jobs"
            results.append({
                "name": "Naukri",
                "title": f"{job_role} - Search on Naukri",
                "company": "Click to view all jobs",
                "url": search_url,
                "description": f"Naukri has strong anti-bot protection. Click to view {job_role} jobs directly on Naukri.com",
                "source": "Naukri (Direct Link)",
                "relevance_score": 50  # Medium score since it's a link, not scraped job
            })
            return results
        
        if 'html_content' not in locals():
            html_content = fetch_html(url, render=True, premium=True)
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Naukri uses dynamic class names - try multiple selectors
        job_cards = soup.find_all('article', class_=re.compile(r'jobTuple|tuple'))
        
        if not job_cards:
            job_cards = soup.find_all('div', class_=re.compile(r'jobTuple|tuple'))
        
        if not job_cards:
            # Try finding any job-related links
            job_cards = soup.find_all('a', href=re.compile(r'/job/|/jobs/'))
            print(f"    [Naukri] Found {len(job_cards)} jobs with fallback selector")
        else:
            print(f"    [Naukri] Found {len(job_cards)} jobs")

        for card in job_cards[:8]:
            try:
                title_elem = card.find('a', class_=re.compile(r'title|job'))
                if not title_elem:
                    title_elem = card.find('a', href=re.compile(r'/job/|/jobs/'))

                if not title_elem:
                    continue

                title = title_elem.text.strip()
                link = title_elem.get('href', '')
                if not link.startswith('http'):
                    link = f"https://www.naukri.com{link}" if link else ""

                company_elem = card.find('a', class_=re.compile(r'compName|company'))
                company = company_elem.text.strip() if company_elem else "Naukri Employer"

                desc_elem = card.find('p', class_=re.compile(r'desc|description'))
                description = desc_elem.text.strip()[:300] if desc_elem else f"Job matching: {query}"

                relevance = calculate_relevance_score(title, description, skills)
                if relevance > 0:
                    results.append({
                        "name": "Naukri",
                        "title": title,
                        "company": company,
                        "url": link,
                        "description": description,
                        "source": "Naukri",
                        "relevance_score": relevance
                    })
            except Exception as e:
                continue
        
        # If no jobs scraped, return direct search link
        if not results:
            print(f"    [Naukri] No jobs scraped, returning search link")
            search_url = f"https://www.naukri.com/{dash_query}-jobs"
            results.append({
                "name": "Naukri",
                "title": f"{job_role} Jobs on Naukri",
                "company": "View All Jobs",
                "url": search_url,
                "description": f"Click to browse {job_role} opportunities directly on Naukri.com",
                "source": "Naukri (Search Link)",
                "relevance_score": 40
            })

        print(f"    [Naukri] Extracted {len(results)} relevant jobs")
    except Exception as e:
        print(f"    [Naukri] Scraping failed: {e}")
        # On error, return direct search link
        job_role = get_naukri_search_role(query)
        dash_query = job_role.replace(' ', '-')
        search_url = f"https://www.naukri.com/{dash_query}-jobs"
        results.append({
            "name": "Naukri",
            "title": f"{job_role} - Browse on Naukri",
            "company": "Click to Search",
            "url": search_url,
            "description": f"Naukri scraping failed. Click to search for {job_role} jobs directly on Naukri.com",
            "source": "Naukri (Fallback)",
            "relevance_score": 30
        })

    return results


def scrape_timesjobs(query, skills, experience_level="", location=""):
    """Scrape actual job listings from TimesJobs."""
    results = []
    try:
        # Map skill to job title
        job_role = get_timesjobs_search_role(query)
        timesjobs_query = urllib.parse.quote(job_role)
        timesjobs_url = f"https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords={timesjobs_query}&txtLocation="
        print(f"    [TimesJobs] Mapped '{query}' -> '{job_role}', navigating to: {timesjobs_url}")
        
        
        
        # Check if blocked
        html_content = fetch_html(url, render=True, premium=True)
        if _is_blocked(html_content):
            print(f"    [TimesJobs] Blocked, returning search link")
            return [_create_fallback_job("TimesJobs", job_role, timesjobs_url, 45)]

        if 'html_content' not in locals():
            html_content = fetch_html(url, render=True, premium=True)
        soup = BeautifulSoup(html_content, "html.parser")
        cards = soup.find_all("li", class_="clearfix job-bx wht-shd-bx")
        
        if not cards:
            cards = soup.find_all("div", class_=re.compile(r'job-listing'))
            print(f"    [TimesJobs] Found {len(cards)} jobs with fallback")
        else:
            print(f"    [TimesJobs] Found {len(cards)} jobs")

        for card in cards[:8]:
            try:
                title_elem = card.find("h2").find("a") if card.find("h2") else None
                if not title_elem:
                    title_elem = card.find("a", href=re.compile(r'/job-details'))
                
                if not title_elem:
                    continue

                title = title_elem.text.strip()
                link = title_elem.get("href", "")
                if not link.startswith('http'):
                    link = f"https://www.timesjobs.com{link}" if link else ""

                company_elem = card.find("h3", class_="joblist-comp-name")
                company = company_elem.text.strip().split("\n")[0] if company_elem else "Various"

                desc_elem = card.find("span", class_="srp-skills")
                description = desc_elem.text.strip()[:300] if desc_elem else f"Job matching: {query}"

                relevance = calculate_relevance_score(title, description, skills)
                if relevance > 0:
                    results.append({
                        "name": "TimesJobs",
                        "title": title,
                        "company": company,
                        "url": link,
                        "description": description,
                        "source": "TimesJobs",
                        "relevance_score": relevance
                    })
            except Exception as e:
                continue
                
        print(f"    [TimesJobs] Extracted {len(results)} relevant jobs")
        
        # If no jobs scraped, return fallback
        if not results:
            job_role = get_timesjobs_search_role(query)
            url = f"https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords={urllib.parse.quote(job_role)}&txtLocation="
            results.append(_create_fallback_job("TimesJobs", job_role, url, 35))
    except Exception as e:
        print(f"    [TimesJobs] Scraping failed: {e}")
        job_role = get_timesjobs_search_role(query)
        url = f"https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords={urllib.parse.quote(job_role)}&txtLocation="
        results.append(_create_fallback_job("TimesJobs", job_role, url, 30, f"TimesJobs scraping failed. Click to search for {job_role} jobs."))

    return results


def scrape_internshala(query, skills, job_type="Full-time", experience_level=""):
    """Scrape actual job listings from Internshala."""
    results = []
    try:
        # Map skill to internship role
        intern_role = get_internshala_search_role(query, job_type)
        internshala_query = "-".join([s.lower().replace(" ", "-") for s in intern_role.split()[:2]])
        base_path = "internships" if job_type == "Internship" else "jobs"
        scrape_url = f"https://internshala.com/{base_path}/keywords-{internshala_query}/"
        print(f"    [Internshala] Mapped '{query}' -> '{intern_role}', navigating to: {scrape_url}")
        
        
        
        # Check if blocked
        html_content = fetch_html(url, render=True, premium=True)
        if _is_blocked(html_content):
            print(f"    [Internshala] Blocked by CAPTCHA, returning search link")
            return [_create_fallback_job("Internshala", intern_role, scrape_url, 45)]

        if 'html_content' not in locals():
            html_content = fetch_html(url, render=True, premium=True)
        soup = BeautifulSoup(html_content, "html.parser")
        cards = soup.find_all("div", class_="internship_meta")
        print(f"    [Internshala] Found {len(cards)} jobs")

        for card in cards[:8]:
            try:
                title_a = card.find("a", class_="job-title-href")
                if not title_a:
                    continue

                title = title_a.text.strip()
                link = "https://internshala.com" + title_a.get("href", "")

                company_elem = card.find("p", class_="company-name")
                company = company_elem.text.strip() if company_elem else "Internshala Partner"

                desc_elem = card.find("div", class_="text")
                description = desc_elem.text.strip()[:300] if desc_elem else f"{job_type} opportunity for {query}"

                relevance = calculate_relevance_score(title, description, skills)
                if relevance > 0:
                    results.append({
                        "name": "Internshala",
                        "title": title,
                        "company": company,
                        "url": link,
                        "description": description,
                        "source": "Internshala",
                        "relevance_score": relevance
                    })
            except Exception as e:
                continue
                
        print(f"    [Internshala] Extracted {len(results)} relevant jobs")
        
        # If no jobs scraped, return fallback
        if not results:
            intern_role = get_internshala_search_role(query, job_type)
            internshala_query = "-".join([s.lower().replace(" ", "-") for s in intern_role.split()[:2]])
            base_path = "internships" if job_type == "Internship" else "jobs"
            url = f"https://internshala.com/{base_path}/keywords-{internshala_query}/"
            results.append(_create_fallback_job("Internshala", intern_role, url, 35))
    except Exception as e:
        print(f"    [Internshala] Scraping failed: {e}")
        intern_role = get_internshala_search_role(query, job_type)
        internshala_query = "-".join([s.lower().replace(" ", "-") for s in intern_role.split()[:2]])
        base_path = "internships" if job_type == "Internship" else "jobs"
        url = f"https://internshala.com/{base_path}/keywords-{internshala_query}/"
        results.append(_create_fallback_job("Internshala", intern_role, url, 30, f"Internshala scraping failed. Click to search for {intern_role} internships/jobs."))

    return results


def scrape_glassdoor(query, skills, experience_level="", location="", page_num=1):
    """
    Scrape actual job listings from Glassdoor.
    Tries multiple expanded job role queries if initial search returns no results.
    Uses experience level and location for better targeting.
    """
    results = []
    try:
        # Get expanded queries for this skill
        search_queries = get_glassdoor_search_queries(query)
        print(f"    [Glassdoor] Trying {len(search_queries)} queries for '{query}': {search_queries[:2]}...")
        
        for search_query in search_queries:
            if results:  # If we already have jobs, stop
                break
            
            # Add location if provided
            full_query = search_query
            if location:
                full_query += f" {location}"
                
            encoded_query = urllib.parse.quote(full_query)
            url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={encoded_query}"
            print(f"    [Glassdoor] Searching: '{full_query}'")
            
            
            
            # Check if blocked
            html_content = fetch_html(url, render=True, premium=True)
        if _is_blocked(html_content):
                print(f"    [Glassdoor] Blocked by CAPTCHA, returning search link")
                return [_create_fallback_job("Glassdoor", search_query, url, 45)]

            if 'html_content' not in locals():
            html_content = fetch_html(url, render=True, premium=True)
        soup = BeautifulSoup(html_content, "html.parser")
            job_cards = soup.find_all('div', class_=re.compile(r'jobListing'))

            if not job_cards:
                job_cards = soup.find_all('li', class_=re.compile(r'JobsList'))
            
            if not job_cards:
                # Fallback: try finding job links directly
                job_cards = soup.find_all('a', href=re.compile(r'/job/'))
            
            print(f"    [Glassdoor] Found {len(job_cards)} jobs for '{search_query}'")

            for card in job_cards[:8]:
                try:
                    title_elem = card.find('a', class_=re.compile(r'jobLink'))
                    if not title_elem:
                        title_elem = card.find('h2').find('a') if card.find('h2') else None
                    
                    if not title_elem:
                        continue

                    title = title_elem.text.strip()
                    link = title_elem.get('href', '')
                    if not link.startswith('http'):
                        link = f"https://www.glassdoor.com{link}" if link else ""

                    company_elem = card.find('a', class_=re.compile(r'company'))
                    company = company_elem.text.strip() if company_elem else "Glassdoor Employer"

                    desc_elem = card.find('div', class_=re.compile(r'jobDescription'))
                    description = desc_elem.text.strip()[:300] if desc_elem else f"Job matching: {query}"

                    relevance = calculate_relevance_score(title, description, skills)
                    if relevance > 0:
                        results.append({
                            "name": "Glassdoor",
                            "title": title,
                            "company": company,
                            "url": link,
                            "description": description,
                            "source": "Glassdoor",
                            "relevance_score": relevance
                        })
                except Exception as e:
                    continue
            
            if not results:
                print(f"    [Glassdoor] No jobs for '{search_query}', trying next query...")
                  # Small delay before next query

        print(f"    [Glassdoor] Extracted {len(results)} relevant jobs for '{query}'")
        
        # If no jobs scraped, return fallback
        if not results:
            job_role = get_glassdoor_search_queries(query)[0]
            url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={urllib.parse.quote(job_role)}"
            results.append(_create_fallback_job("Glassdoor", job_role, url, 35))
    except Exception as e:
        print(f"    [Glassdoor] Scraping failed: {e}")
        job_role = get_glassdoor_search_queries(query)[0]
        url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={urllib.parse.quote(job_role)}"
        results.append(_create_fallback_job("Glassdoor", job_role, url, 30, f"Glassdoor scraping failed. Click to search for {job_role} jobs."))

    return results


def scrape_monster(query, skills, experience_level="", location=""):
    """
    Scrape actual job listings from Monster (foundit.in).
    Maps skills to traditional corporate job titles for better results.
    Uses location for better targeting.
    """
    results = []
    try:
        # Map skill to traditional corporate job role
        job_role = get_monster_search_role(query)
        
        # Add location to query
        search_query = job_role
        if location:
            search_query += f" {location}"
        
        encoded_query = urllib.parse.quote(search_query)
        url = f"https://www.foundit.in/srp/results?query={encoded_query}"
        print(f"    [Monster] Mapped '{query}' -> '{search_query}', navigating to: {url}")
        
        
        
        # Check if blocked
        html_content = fetch_html(url, render=True, premium=True)
        if _is_blocked(html_content):
            print(f"    [Monster] Blocked by anti-bot, returning search link")
            return [_create_fallback_job("Monster", job_role, url, 45)]

        if 'html_content' not in locals():
            html_content = fetch_html(url, render=True, premium=True)
        soup = BeautifulSoup(html_content, "html.parser")
        job_cards = soup.find_all('div', class_=re.compile(r'SearchJob'))

        if not job_cards:
            job_cards = soup.find_all('div', class_=re.compile(r'job-card'))
            print(f"    [Monster] Found {len(job_cards)} jobs with fallback")
        else:
            print(f"    [Monster] Found {len(job_cards)} jobs")

        for card in job_cards[:8]:
            try:
                title_elem = card.find('h2').find('a') if card.find('h2') else None
                if not title_elem:
                    title_link = card.find('a', href=re.compile(r'/job-details'))
                    if not title_link:
                        continue
                    title = title_link.text.strip()
                    link = title_link.get('href', '')
                else:
                    title = title_elem.text.strip()
                    link = title_elem.get('href', '')

                company_elem = card.find('a', class_=re.compile(r'Company'))
                company = company_elem.text.strip() if company_elem else "Monster Employer"

                desc_elem = card.find('p', class_=re.compile(r'[Jj]ob'))
                description = desc_elem.text.strip()[:300] if desc_elem else f"Job matching: {query}"

                relevance = calculate_relevance_score(title, description, skills)
                if relevance > 0:
                    results.append({
                        "name": "Monster",
                        "title": title,
                        "company": company,
                        "url": link if link else "#",
                        "description": description,
                        "source": "Monster",
                        "relevance_score": relevance
                    })
            except Exception as e:
                continue

        print(f"    [Monster] Extracted {len(results)} relevant jobs")
        
        # If no jobs scraped, return fallback
        if not results:
            job_role = get_monster_search_role(query)
            url = f"https://www.foundit.in/srp/results?query={urllib.parse.quote(job_role)}"
            results.append(_create_fallback_job("Monster", job_role, url, 35))
    except Exception as e:
        print(f"    [Monster] Scraping failed: {e}")
        job_role = get_monster_search_role(query)
        url = f"https://www.foundit.in/srp/results?query={urllib.parse.quote(job_role)}"
        results.append(_create_fallback_job("Monster", job_role, url, 30, f"Monster scraping failed. Click to search for {job_role} jobs."))

    return results


def scrape_wellfound(query, skills, experience_level=""):
    """
    Scrape actual job listings from Wellfound (AngelList).
    Maps technical skills to proper startup job roles for better results.
    """
    results = []
    try:
        # Map skill to proper startup job role
        job_role = get_wellfound_search_role(query)
        # Fix: Wellfound uses /role/[role-slug], NOT /role/l/[role-slug]
        dash_query = job_role.replace(' ', '-').lower()
        url = f"https://wellfound.com/role/{dash_query}"
        print(f"    [Wellfound] Mapped '{query}' -> '{job_role}', navigating to: {url}")
        
        
        
        # Check if blocked
        html_content = fetch_html(url, render=True, premium=True)
        if _is_blocked(html_content):
            print(f"    [Wellfound] Blocked by CAPTCHA, returning search link")
            return [_create_fallback_job("Wellfound", job_role, url, 45)]

        if 'html_content' not in locals():
            html_content = fetch_html(url, render=True, premium=True)
        soup = BeautifulSoup(html_content, "html.parser")
        job_cards = soup.find_all('div', class_=re.compile(r'styles__JobCard'))

        if not job_cards:
            job_cards = soup.find_all('a', href=re.compile(r'/jobs/'))
            print(f"    [Wellfound] Found {len(job_cards)} jobs with fallback")
        else:
            print(f"    [Wellfound] Found {len(job_cards)} jobs")

        for card in job_cards[:8]:
            try:
                title_elem = card.find('a', href=re.compile(r'/jobs'))
                if not title_elem:
                    continue

                title = title_elem.text.strip()
                link = title_elem.get('href', '')
                if not link.startswith('http'):
                    link = f"https://wellfound.com{link}" if link else ""

                company_elem = card.find('div', class_=re.compile(r'styles__Company'))
                company = company_elem.text.strip() if company_elem else "Wellfound Startup"

                description = f"Startup opportunity for {query}"

                relevance = calculate_relevance_score(title, description, skills)
                if relevance > 0:
                    results.append({
                        "name": "Wellfound",
                        "title": title,
                        "company": company,
                        "url": link,
                        "description": description,
                        "source": "Wellfound",
                        "relevance_score": relevance
                    })
            except Exception as e:
                continue

        print(f"    [Wellfound] Extracted {len(results)} relevant jobs")
        
        # If no jobs scraped, return fallback
        if not results:
            job_role = get_wellfound_search_role(query)
            url = f"https://wellfound.com/role/{job_role.replace(' ', '-').lower()}"
            results.append(_create_fallback_job("Wellfound", job_role, url, 35))
    except Exception as e:
        print(f"    [Wellfound] Scraping failed: {e}")
        job_role = get_wellfound_search_role(query)
        url = f"https://wellfound.com/role/{job_role.replace(' ', '-').lower()}"
        results.append(_create_fallback_job("Wellfound", job_role, url, 30, f"Wellfound scraping failed. Click to search for {job_role} startup jobs."))

    return results


def scrape_upwork(query, skills):
    """Scrape actual job listings from Upwork."""
    results = []
    try:
        # Map skill to freelance job title
        job_role = get_upwork_search_role(query)
        encoded_query = urllib.parse.quote(job_role)
        url = f"https://www.upwork.com/nx/search/jobs/?q={encoded_query}"
        print(f"    [Upwork] Mapped '{query}' -> '{job_role}', navigating to: {url}")
        
        
        
        # Check if blocked
        html_content = fetch_html(url, render=True, premium=True)
        if _is_blocked(html_content):
            print(f"    [Upwork] Blocked, returning search link")
            return [_create_fallback_job("Upwork", job_role, url, 45)]

        if 'html_content' not in locals():
            html_content = fetch_html(url, render=True, premium=True)
        soup = BeautifulSoup(html_content, "html.parser")
        job_cards = soup.find_all('div', class_=re.compile(r'JobTile'))
        
        if not job_cards:
            job_cards = soup.find_all('a', class_=re.compile(r'job-title'))
            print(f"    [Upwork] Found {len(job_cards)} jobs with fallback")
        else:
            print(f"    [Upwork] Found {len(job_cards)} jobs")

        for card in job_cards[:8]:
            try:
                title_elem = card.find('a', class_=re.compile(r'visit'))
                if not title_elem:
                    title_elem = card.find('h3').find('a') if card.find('h3') else None

                if not title_elem:
                    continue

                title = title_elem.text.strip()
                link = title_elem.get('href', '')
                if not link.startswith('http'):
                    link = f"https://www.upwork.com{link}" if link else ""

                desc_elem = card.find('p', class_=re.compile(r'[Dd]escription'))
                description = desc_elem.text.strip()[:300] if desc_elem else f"Freelance opportunity for {query}"

                relevance = calculate_relevance_score(title, description, skills)
                if relevance > 0:
                    results.append({
                        "name": "Upwork",
                        "title": title,
                        "company": "Upwork Client",
                        "url": link,
                        "description": description,
                        "source": "Upwork",
                        "relevance_score": relevance
                    })
            except Exception as e:
                continue
                
        print(f"    [Upwork] Extracted {len(results)} relevant jobs")
        
        # If no jobs scraped, return fallback
        if not results:
            job_role = get_upwork_search_role(query)
            url = f"https://www.upwork.com/nx/search/jobs/?q={urllib.parse.quote(job_role)}"
            results.append(_create_fallback_job("Upwork", job_role, url, 35))
    except Exception as e:
        print(f"    [Upwork] Scraping failed: {e}")
        job_role = get_upwork_search_role(query)
        url = f"https://www.upwork.com/nx/search/jobs/?q={urllib.parse.quote(job_role)}"
        results.append(_create_fallback_job("Upwork", job_role, url, 30, f"Upwork scraping failed. Click to search for {job_role} freelance jobs."))

    return results


def scrape_dice(query, skills, location=""):
    """Scrape actual job listings from Dice.com (Tech jobs)."""
    results = []
    try:
        # Map skill to tech job role
        job_role = get_indeed_search_role(query)  # Use same mappings
        
        # Add location
        search_query = job_role
        if location:
            search_query += f" {location}"
        
        encoded_query = urllib.parse.quote(search_query)
        url = f"https://www.dice.com/jobs?q={encoded_query}"
        print(f"    [Dice] Mapped '{query}' -> '{search_query}', navigating to: {url}")
        
        
        
        # Check if blocked
        html_content = fetch_html(url, render=True, premium=True)
        if _is_blocked(html_content):
            print(f"    [Dice] Blocked, returning search link")
            return [_create_fallback_job("Dice", job_role, url, 45)]

        if 'html_content' not in locals():
            html_content = fetch_html(url, render=True, premium=True)
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Dice uses card-based layout
        job_cards = soup.find_all('div', class_=re.compile(r'card-content'))
        
        if not job_cards:
            job_cards = soup.find_all('article', class_=re.compile(r'job'))
        
        if not job_cards:
            job_cards = soup.find_all('a', href=re.compile(r'/job-view/'))
            print(f"    [Dice] Found {len(job_cards)} jobs with fallback")
        else:
            print(f"    [Dice] Found {len(job_cards)} jobs")

        for card in job_cards[:8]:
            try:
                title_elem = card.find('a', class_=re.compile(r'title'))
                if not title_elem:
                    title_elem = card.find('h2').find('a') if card.find('h2') else None
                
                if not title_elem:
                    continue

                title = title_elem.text.strip()
                link = title_elem.get('href', '')
                if not link.startswith('http'):
                    link = f"https://www.dice.com{link}" if link else ""

                company_elem = card.find('a', class_=re.compile(r'company'))
                company = company_elem.text.strip() if company_elem else "Dice Employer"

                desc_elem = card.find('p', class_=re.compile(r'[Dd]escription'))
                description = desc_elem.text.strip()[:300] if desc_elem else f"Tech job matching: {query}"

                relevance = calculate_relevance_score(title, description, skills)
                if relevance > 0:
                    results.append({
                        "name": "Dice",
                        "title": title,
                        "company": company,
                        "url": link,
                        "description": description,
                        "source": "Dice",
                        "relevance_score": relevance
                    })
            except Exception as e:
                continue

        print(f"    [Dice] Extracted {len(results)} relevant jobs")
        
        # If no jobs scraped, return fallback
        if not results:
            job_role = get_indeed_search_role(query)
            url = f"https://www.dice.com/jobs?q={urllib.parse.quote(job_role)}"
            results.append(_create_fallback_job("Dice", job_role, url, 35))
    except Exception as e:
        print(f"    [Dice] Scraping failed: {e}")
        job_role = get_indeed_search_role(query)
        url = f"https://www.dice.com/jobs?q={urllib.parse.quote(job_role)}"
        results.append(_create_fallback_job("Dice", job_role, url, 30, f"Dice scraping failed. Click to search for {job_role} tech jobs."))

    return results


def scrape_weworkremotely(query, skills):
    """Scrape actual job listings from WeWorkRemotely (Remote jobs)."""
    results = []
    try:
        # Map skill to remote job role
        job_role = get_upwork_search_role(query)  # Use freelance mappings for remote
        dash_query = job_role.replace(' ', '-').lower()
        url = f"https://weworkremotely.com/remote-jobs/search?term={dash_query}"
        print(f"    [WeWorkRemotely] Mapped '{query}' -> '{job_role}', navigating to: {url}")
        
        

        if 'html_content' not in locals():
            html_content = fetch_html(url, render=True, premium=True)
        soup = BeautifulSoup(html_content, "html.parser")
        
        # WeWorkRemotely uses list-based layout
        job_cards = soup.find_all('li', class_=re.compile(r'job'))
        
        if not job_cards:
            job_cards = soup.find_all('a', class_=re.compile(r'job'))
            print(f"    [WeWorkRemotely] Found {len(job_cards)} jobs with fallback")
        else:
            print(f"    [WeWorkRemotely] Found {len(job_cards)} jobs")

        for card in job_cards[:8]:
            try:
                title_elem = card.find('a', class_=re.compile(r'job'))
                if not title_elem:
                    title_elem = card.find('span', class_=re.compile(r'title'))
                
                if not title_elem:
                    continue

                title = title_elem.text.strip()
                link = title_elem.get('href', '')
                if not link.startswith('http'):
                    link = f"https://weworkremotely.com{link}" if link else ""

                company_elem = card.find('span', class_=re.compile(r'company'))
                company = company_elem.text.strip() if company_elem else "Remote Employer"

                description = f"Remote opportunity for {query}"

                relevance = calculate_relevance_score(title, description, skills)
                if relevance > 0:
                    results.append({
                        "name": "WeWorkRemotely",
                        "title": title,
                        "company": company,
                        "url": link,
                        "description": description,
                        "source": "WeWorkRemotely",
                        "relevance_score": relevance
                    })
            except Exception as e:
                continue

        print(f"    [WeWorkRemotely] Extracted {len(results)} relevant jobs")
    except Exception as e:
        print(f"    [WeWorkRemotely] Scraping failed: {e}")

    return results


# ============ NEW SCRAPERS FOR JOB-TYPE SPECIFIC SITES ============

def scrape_flexjobs(query, skills, experience_level="", location=""):
    """Scrape FlexJobs for part-time/remote opportunities."""
    results = []
    try:
        job_role = get_linkedin_search_role(query)
        search_parts = [job_role, "Part-Time"]
        if location:
            search_parts.append(location)
        search_query = ' '.join(search_parts)
        encoded_query = urllib.parse.quote(search_query)
        url = f"https://www.flexjobs.com/search?search={encoded_query}&schedule=Part-Time"

        print(f"    [FlexJobs] Searching for '{search_query}'")
        
        

        html_content = fetch_html(url, render=True, premium=True)
        if _is_blocked(html_content):
            print(f"    [FlexJobs] Blocked, returning search link")
            return [_create_fallback_job("FlexJobs", job_role, url, 45)]

        if 'html_content' not in locals():
            html_content = fetch_html(url, render=True, premium=True)
        soup = BeautifulSoup(html_content, "html.parser")
        job_cards = soup.find_all('div', class_=re.compile(r'job|listing|search-result', re.I))

        if not job_cards:
            job_cards = soup.find_all('li', class_=re.compile(r'job|listing', re.I))

        for card in job_cards[:10]:
            try:
                title_elem = card.find('a', class_=re.compile(r'job|title|link', re.I))
                if not title_elem:
                    continue
                title = title_elem.text.strip()
                link = title_elem.get('href', '')
                if not link.startswith('http'):
                    link = f"https://www.flexjobs.com{link}" if link else url

                company_elem = card.find(class_=re.compile(r'company|employer', re.I))
                company = company_elem.text.strip() if company_elem else "Various Employers"

                desc_elem = card.find(class_=re.compile(r'description|snippet', re.I))
                description = desc_elem.text.strip()[:300] if desc_elem else f"Part-time {query} opportunity"

                relevance = calculate_relevance_score(title, description, skills)
                if relevance > 0:
                    results.append({
                        "name": "FlexJobs",
                        "title": title,
                        "company": company,
                        "url": link,
                        "description": description,
                        "source": "FlexJobs",
                        "relevance_score": relevance
                    })
            except Exception:
                continue

        if not results:
            results.append(_create_fallback_job("FlexJobs", job_role, url, 35))
        print(f"    [FlexJobs] Extracted {len(results)} relevant jobs")
    except Exception as e:
        print(f"    [FlexJobs] Scraping failed: {e}")
        job_role = get_linkedin_search_role(query)
        results.append(_create_fallback_job("FlexJobs", job_role, f"https://www.flexjobs.com/search?search={urllib.parse.quote(query)}", 30))

    return results


def scrape_apna(query, skills, experience_level="", location=""):
    """Scrape Apna.co for part-time/local jobs."""
    results = []
    try:
        job_role = get_indeed_search_role(query)
        encoded_query = urllib.parse.quote(job_role)
        location_query = urllib.parse.quote(location) if location else ""
        url = f"https://apna.co/search/{encoded_query}"
        if location_query:
            url += f"?city={location_query}"

        print(f"    [Apna] Searching for '{job_role}'")
        
        

        html_content = fetch_html(url, render=True, premium=True)
        if _is_blocked(html_content):
            print(f"    [Apna] Blocked, returning search link")
            return [_create_fallback_job("Apna", job_role, url, 45)]

        if 'html_content' not in locals():
            html_content = fetch_html(url, render=True, premium=True)
        soup = BeautifulSoup(html_content, "html.parser")
        job_cards = soup.find_all('div', class_=re.compile(r'job|card|listing', re.I))

        for card in job_cards[:10]:
            try:
                title_elem = card.find('a') or card.find('h3')
                if not title_elem:
                    continue
                title = title_elem.text.strip()
                link = title_elem.get('href', '')
                if not link.startswith('http'):
                    link = f"https://apna.co{link}" if link else url

                company_elem = card.find(class_=re.compile(r'company|employer|org', re.I))
                company = company_elem.text.strip() if company_elem else "Company"

                description = f"{query} opportunity on Apna"
                relevance = calculate_relevance_score(title, description, skills)
                if relevance > 0:
                    results.append({
                        "name": "Apna",
                        "title": title,
                        "company": company,
                        "url": link,
                        "description": description,
                        "source": "Apna",
                        "relevance_score": relevance
                    })
            except Exception:
                continue

        if not results:
            results.append(_create_fallback_job("Apna", job_role, url, 35))
        print(f"    [Apna] Extracted {len(results)} relevant jobs")
    except Exception as e:
        print(f"    [Apna] Scraping failed: {e}")
        job_role = get_indeed_search_role(query)
        results.append(_create_fallback_job("Apna", job_role, f"https://apna.co/search/{urllib.parse.quote(query)}", 30))

    return results


def scrape_snagajob(query, skills, experience_level="", location=""):
    """Scrape Snagajob for part-time/hourly work."""
    results = []
    try:
        job_role = get_indeed_search_role(query)
        encoded_query = urllib.parse.quote(f"{job_role} part time")
        location_param = urllib.parse.quote(location) if location else ""
        url = f"https://www.snagajob.com/search?w={encoded_query}"
        if location_param:
            url += f"&l={location_param}"

        print(f"    [Snagajob] Searching for '{job_role} part time'")
        
        

        html_content = fetch_html(url, render=True, premium=True)
        if _is_blocked(html_content):
            return [_create_fallback_job("Snagajob", job_role, url, 45)]

        if 'html_content' not in locals():
            html_content = fetch_html(url, render=True, premium=True)
        soup = BeautifulSoup(html_content, "html.parser")
        job_cards = soup.find_all('div', class_=re.compile(r'job|card|result', re.I))

        for card in job_cards[:10]:
            try:
                title_elem = card.find('a')
                if not title_elem:
                    continue
                title = title_elem.text.strip()
                link = title_elem.get('href', '')
                if not link.startswith('http'):
                    link = f"https://www.snagajob.com{link}" if link else url

                company_elem = card.find(class_=re.compile(r'company|employer', re.I))
                company = company_elem.text.strip() if company_elem else "Employer"

                description = f"Part-time {query} position"
                relevance = calculate_relevance_score(title, description, skills)
                if relevance > 0:
                    results.append({
                        "name": "Snagajob",
                        "title": title,
                        "company": company,
                        "url": link,
                        "description": description,
                        "source": "Snagajob",
                        "relevance_score": relevance
                    })
            except Exception:
                continue

        if not results:
            results.append(_create_fallback_job("Snagajob", job_role, url, 35))
        print(f"    [Snagajob] Extracted {len(results)} relevant jobs")
    except Exception as e:
        print(f"    [Snagajob] Scraping failed: {e}")
        job_role = get_indeed_search_role(query)
        results.append(_create_fallback_job("Snagajob", job_role, f"https://www.snagajob.com/search?w={urllib.parse.quote(query)}", 30))

    return results


def scrape_unstop(query, skills, job_type="", experience_level=""):
    """Scrape Unstop for internships and early career roles."""
    results = []
    try:
        job_role = get_internshala_search_role(query, job_type)
        encoded_query = urllib.parse.quote(job_role)
        url = f"https://unstop.com/internships?q={encoded_query}"

        print(f"    [Unstop] Searching for '{job_role}' internships")
        
        

        html_content = fetch_html(url, render=True, premium=True)
        if _is_blocked(html_content):
            return [_create_fallback_job("Unstop", job_role, url, 45)]

        if 'html_content' not in locals():
            html_content = fetch_html(url, render=True, premium=True)
        soup = BeautifulSoup(html_content, "html.parser")
        job_cards = soup.find_all('div', class_=re.compile(r'card|listing|internship', re.I))

        if not job_cards:
            job_cards = soup.find_all('a', class_=re.compile(r'card|link', re.I))

        for card in job_cards[:10]:
            try:
                title_elem = card.find('h3') or card.find('h4') or card.find('a')
                if not title_elem:
                    continue
                title = title_elem.text.strip()
                link = card.get('href', '')
                if not link.startswith('http'):
                    link = f"https://unstop.com{link}" if link else url

                company_elem = card.find(class_=re.compile(r'company|employer|organization', re.I))
                company = company_elem.text.strip() if company_elem else "Company"

                description = f"Internship opportunity in {query}"
                relevance = calculate_relevance_score(title, description, skills)
                if relevance > 0:
                    results.append({
                        "name": "Unstop",
                        "title": title,
                        "company": company,
                        "url": link,
                        "description": description,
                        "source": "Unstop",
                        "relevance_score": relevance
                    })
            except Exception:
                continue

        if not results:
            results.append(_create_fallback_job("Unstop", job_role, url, 35))
        print(f"    [Unstop] Extracted {len(results)} relevant jobs")
    except Exception as e:
        print(f"    [Unstop] Scraping failed: {e}")
        job_role = get_internshala_search_role(query)
        results.append(_create_fallback_job("Unstop", job_role, f"https://unstop.com/internships?q={urllib.parse.quote(query)}", 30))

    return results


def scrape_wayup(query, skills, job_type="", experience_level=""):
    """Scrape WayUp for internships and entry-level roles."""
    results = []
    try:
        job_role = get_internshala_search_role(query, job_type)
        dash_query = job_role.lower().replace(' ', '-')
        url = f"https://www.wayup.com/s/internships/{dash_query}/"

        print(f"    [WayUp] Searching for '{job_role}' internships")
        
        

        html_content = fetch_html(url, render=True, premium=True)
        if _is_blocked(html_content):
            return [_create_fallback_job("WayUp", job_role, url, 45)]

        if 'html_content' not in locals():
            html_content = fetch_html(url, render=True, premium=True)
        soup = BeautifulSoup(html_content, "html.parser")
        job_cards = soup.find_all('div', class_=re.compile(r'card|job|listing|result', re.I))

        for card in job_cards[:10]:
            try:
                title_elem = card.find('a')
                if not title_elem:
                    continue
                title = title_elem.text.strip()
                link = title_elem.get('href', '')
                if not link.startswith('http'):
                    link = f"https://www.wayup.com{link}" if link else url

                company_elem = card.find(class_=re.compile(r'company|employer|organization', re.I))
                company = company_elem.text.strip() if company_elem else "Company"

                description = f"Internship/entry-level {query} opportunity"
                relevance = calculate_relevance_score(title, description, skills)
                if relevance > 0:
                    results.append({
                        "name": "WayUp",
                        "title": title,
                        "company": company,
                        "url": link,
                        "description": description,
                        "source": "WayUp",
                        "relevance_score": relevance
                    })
            except Exception:
                continue

        if not results:
            results.append(_create_fallback_job("WayUp", job_role, url, 35))
        print(f"    [WayUp] Extracted {len(results)} relevant jobs")
    except Exception as e:
        print(f"    [WayUp] Scraping failed: {e}")
        job_role = get_internshala_search_role(query)
        results.append(_create_fallback_job("WayUp", job_role, f"https://www.wayup.com/s/internships/{query.lower().replace(' ', '-')}", 30))

    return results


def scrape_freelancer(query, skills, experience_level="", location=""):
    """Scrape Freelancer.com for freelance projects."""
    results = []
    try:
        job_role = get_upwork_search_role(query)
        encoded_query = urllib.parse.quote(job_role)
        url = f"https://www.freelancer.com/jobs/?keyword={encoded_query}"

        print(f"    [Freelancer] Searching for '{job_role}' projects")
        
        

        html_content = fetch_html(url, render=True, premium=True)
        if _is_blocked(html_content):
            return [_create_fallback_job("Freelancer", job_role, url, 45)]

        if 'html_content' not in locals():
            html_content = fetch_html(url, render=True, premium=True)
        soup = BeautifulSoup(html_content, "html.parser")
        job_cards = soup.find_all('div', class_=re.compile(r'SearchResult|job|listing', re.I))

        if not job_cards:
            job_cards = soup.find_all('div', id=re.compile(r'SearchResult', re.I))

        for card in job_cards[:10]:
            try:
                title_elem = card.find('a', class_=re.compile(r'SearchResult', re.I)) or card.find('a')
                if not title_elem:
                    continue
                title = title_elem.text.strip()
                link = title_elem.get('href', '')
                if not link.startswith('http'):
                    link = f"https://www.freelancer.com{link}" if link else url

                desc_elem = card.find(class_=re.compile(r'description|Snippet', re.I))
                description = desc_elem.text.strip()[:300] if desc_elem else f"Freelance {query} project"

                relevance = calculate_relevance_score(title, description, skills)
                if relevance > 0:
                    results.append({
                        "name": "Freelancer",
                        "title": title,
                        "company": "Client",
                        "url": link,
                        "description": description,
                        "source": "Freelancer",
                        "relevance_score": relevance
                    })
            except Exception:
                continue

        if not results:
            results.append(_create_fallback_job("Freelancer", job_role, url, 35))
        print(f"    [Freelancer] Extracted {len(results)} relevant jobs")
    except Exception as e:
        print(f"    [Freelancer] Scraping failed: {e}")
        job_role = get_upwork_search_role(query)
        results.append(_create_fallback_job("Freelancer", job_role, f"https://www.freelancer.com/jobs/?keyword={urllib.parse.quote(query)}", 30))

    return results


def scrape_fiverr(query, skills, experience_level="", location=""):
    """Scrape Fiverr for freelance gigs (search as buyer looking for gigs or as seller opportunity)."""
    results = []
    try:
        job_role = get_upwork_search_role(query)
        encoded_query = urllib.parse.quote(job_role)
        url = f"https://www.fiverr.com/search/gigs?query={encoded_query}"

        print(f"    [Fiverr] Searching for '{job_role}' gigs")
        
        

        html_content = fetch_html(url, render=True, premium=True)
        if _is_blocked(html_content):
            return [_create_fallback_job("Fiverr", job_role, url, 45)]

        if 'html_content' not in locals():
            html_content = fetch_html(url, render=True, premium=True)
        soup = BeautifulSoup(html_content, "html.parser")
        gig_cards = soup.find_all('div', class_=re.compile(r'gig|card|listing', re.I))

        if not gig_cards:
            gig_cards = soup.find_all('li', class_=re.compile(r'gig|card', re.I))

        for card in gig_cards[:10]:
            try:
                title_elem = card.find('a')
                if not title_elem:
                    continue
                title = title_elem.text.strip()
                link = title_elem.get('href', '')
                if not link.startswith('http'):
                    link = f"https://www.fiverr.com{link}" if link else url

                seller_elem = card.find(class_=re.compile(r'seller|username|author', re.I))
                seller = seller_elem.text.strip() if seller_elem else "Various Sellers"

                description = f"Freelance {query} service/gig opportunity"
                relevance = calculate_relevance_score(title, description, skills)
                if relevance > 0:
                    results.append({
                        "name": "Fiverr",
                        "title": title,
                        "company": seller,
                        "url": link,
                        "description": description,
                        "source": "Fiverr",
                        "relevance_score": relevance
                    })
            except Exception:
                continue

        if not results:
            results.append(_create_fallback_job("Fiverr", job_role, url, 35))
        print(f"    [Fiverr] Extracted {len(results)} relevant jobs")
    except Exception as e:
        print(f"    [Fiverr] Scraping failed: {e}")
        job_role = get_upwork_search_role(query)
        results.append(_create_fallback_job("Fiverr", job_role, f"https://www.fiverr.com/search/gigs?query={urllib.parse.quote(query)}", 30))

    return results


def scrape_peopleperhour(query, skills, experience_level="", location=""):
    """Scrape PeoplePerHour for freelance jobs."""
    results = []
    try:
        job_role = get_upwork_search_role(query)
        encoded_query = urllib.parse.quote(job_role)
        url = f"https://www.peopleperhour.com/freelance-jobs?q={encoded_query}"

        print(f"    [PeoplePerHour] Searching for '{job_role}'")
        
        

        html_content = fetch_html(url, render=True, premium=True)
        if _is_blocked(html_content):
            return [_create_fallback_job("PeoplePerHour", job_role, url, 45)]

        if 'html_content' not in locals():
            html_content = fetch_html(url, render=True, premium=True)
        soup = BeautifulSoup(html_content, "html.parser")
        job_cards = soup.find_all('div', class_=re.compile(r'job|listing|card|hoverable', re.I))

        if not job_cards:
            job_cards = soup.find_all('li', class_=re.compile(r'job|listing', re.I))

        for card in job_cards[:10]:
            try:
                title_elem = card.find('a')
                if not title_elem:
                    continue
                title = title_elem.text.strip()
                link = title_elem.get('href', '')
                if not link.startswith('http'):
                    link = f"https://www.peopleperhour.com{link}" if link else url

                company_elem = card.find(class_=re.compile(r'company|buyer|employer', re.I))
                company = company_elem.text.strip() if company_elem else "Client"

                desc_elem = card.find(class_=re.compile(r'description|snippet', re.I))
                description = desc_elem.text.strip()[:300] if desc_elem else f"Freelance {query} opportunity"

                relevance = calculate_relevance_score(title, description, skills)
                if relevance > 0:
                    results.append({
                        "name": "PeoplePerHour",
                        "title": title,
                        "company": company,
                        "url": link,
                        "description": description,
                        "source": "PeoplePerHour",
                        "relevance_score": relevance
                    })
            except Exception:
                continue

        if not results:
            results.append(_create_fallback_job("PeoplePerHour", job_role, url, 35))
        print(f"    [PeoplePerHour] Extracted {len(results)} relevant jobs")
    except Exception as e:
        print(f"    [PeoplePerHour] Scraping failed: {e}")
        job_role = get_upwork_search_role(query)
        results.append(_create_fallback_job("PeoplePerHour", job_role, f"https://www.peopleperhour.com/freelance-jobs?q={urllib.parse.quote(query)}", 30))

    return results


def scrape_toptal(query, skills, experience_level="", location=""):
    """Scrape Toptal for high-end freelance roles (or provide fallback link)."""
    results = []
    try:
        job_role = get_upwork_search_role(query)
        # Toptal is an application-based platform, so we provide a direct link
        url = f"https://www.toptal.com/{query.lower().replace(' ', '-')}"

        print(f"    [Toptal] Providing link for '{job_role}'")
        
        

        html_content = fetch_html(url, render=True, premium=True)
        if _is_blocked(html_content):
            return [_create_fallback_job("Toptal", job_role, url, 45)]

        # Toptal doesn't have a traditional job board, it's talent-matching
        # Provide a well-structured fallback link
        results.append(_create_fallback_job("Toptal", job_role, url, 40,
            f"Toptal matches top 3% of freelance talent. Apply to join the Toptal network for {job_role} opportunities."))

        print(f"    [Toptal] Returned talent network link")
    except Exception as e:
        print(f"    [Toptal] Failed: {e}")
        job_role = get_upwork_search_role(query)
        results.append(_create_fallback_job("Toptal", job_role, f"https://www.toptal.com", 30))

    return results


def get_dynamic_job_links(skills, level, job_type="Full-time", experience_level="", location="", job_role=""):
    """
    Dynamically scrapes actual job postings from multiple websites.
    For EACH specific job role inferred from skills, it searches EACH website.
    It scrapes 2 pages of results, evaluates ALL jobs against the user's specific skills,
    and returns ONLY the single absolute best match per site, per role.
    """
    if not skills:
        return []

    if not job_role:
        from analyzer import infer_job_role
        job_role = infer_job_role(skills)

    # Roles can be comma-separated from the analyzer
    roles_to_search = [r.strip() for r in job_role.split(",") if r.strip()]
    if not roles_to_search:
        roles_to_search = ["Software Developer"] # fallback

    # Combine all sites across all job types to ensure we search 11+ websites
    all_possible_sites = []
    for sites in JOB_TYPE_SITES.values():
        all_possible_sites.extend(sites)
    
    # Add other scrapers that might not be in the default mapping
    all_possible_sites.extend([
        "TimesJobs", "Upwork", "FlexJobs", "Apna", "Snagajob", "Unstop", 
        "WayUp", "Freelancer", "Fiverr", "PeoplePerHour", "Toptal"
    ])
    
    # Remove duplicates but keep a consistent order
    sites_to_scrape = list(dict.fromkeys(all_possible_sites))
    
    print(f"\n🎯 Job Type: {job_type}")
    print(f"📋 Found Roles: {', '.join(roles_to_search)}")
    print(f"📋 Scraping {len(sites_to_scrape)} sites: {', '.join(sites_to_scrape)}")

    best_jobs_overall = []
    seen_urls = set()

    if True:
        browser = None
        context = None AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 720}
        )
        page = None
        

        # Set longer timeout for slow sites
          # 30 seconds

        # Iterate through EACH job role
        for role_idx, role in enumerate(roles_to_search):
            print(f"\n=======================================================")
            print(f"=== Deep Search for Role #{role_idx + 1}/{len(roles_to_search)}: '{role}' ===")
            print(f"    Experience: {experience_level or level}, Location: {location or 'Any'}")
            print(f"=======================================================")

            # For this specific role, check each site
            for scraper_name in sites_to_scrape:
                print(f"\n  🔄 Deep Scraping {scraper_name} for '{role}'...")
                
                # We will collect all jobs from pages 1 and 2 for this specific role on this specific site
                all_jobs_for_this_site_and_role = []
                
                # Search across 2 pages
                for page_num in [1, 2]:
                    # Define ALL possible scrapers, passing the ROLE as the query
                    all_scrapers = {
                        "Indeed": lambda: scrape_indeed(role, skills, experience_level or level, location, page_num),
                        "LinkedIn": lambda: scrape_linkedin(role, skills, experience_level or level, location, page_num),
                        "TimesJobs": lambda: scrape_timesjobs(role, skills, experience_level or level, location), # TimesJobs doesn't support page_num well
                        "Naukri": lambda: scrape_naukri(role, skills, experience_level or level, location, page_num),
                        "Internshala": lambda: scrape_internshala(role, skills, job_type, experience_level or level), # Internshala doesn't support page_num well
                        "Glassdoor": lambda: scrape_glassdoor(role, skills, experience_level or level, location, page_num),
                        "Monster": lambda: scrape_monster(role, skills, experience_level or level, location), # Monster doesn't support page_num well
                        "Wellfound": lambda: scrape_wellfound(role, skills, experience_level or level), # Wellfound doesn't support page_num well
                        "Upwork": lambda: scrape_upwork(role, skills),
                        "Dice": lambda: scrape_dice(role, skills, location),
                        "WeWorkRemotely": lambda: scrape_weworkremotely(role, skills),
                        "FlexJobs": lambda: scrape_flexjobs(role, skills, experience_level or level, location),
                        "Apna": lambda: scrape_apna(role, skills, experience_level or level, location),
                        "Snagajob": lambda: scrape_snagajob(role, skills, experience_level or level, location),
                        "Unstop": lambda: scrape_unstop(role, skills, job_type, experience_level or level),
                        "WayUp": lambda: scrape_wayup(role, skills, job_type, experience_level or level),
                        "Freelancer": lambda: scrape_freelancer(role, skills, experience_level or level, location),
                        "Fiverr": lambda: scrape_fiverr(role, skills, experience_level or level, location),
                        "PeoplePerHour": lambda: scrape_peopleperhour(role, skills, experience_level or level, location),
                        "Toptal": lambda: scrape_toptal(role, skills, experience_level or level, location),
                    }

                    if scraper_name not in all_scrapers:
                        continue

                    # If page_num is 2 and the site doesn't actually paginate in our scraper, skip page 2
                    non_paginating_sites = ["TimesJobs", "Internshala", "Monster", "Wellfound", "Upwork", "Dice", "WeWorkRemotely", "FlexJobs", "Apna", "Snagajob", "Unstop", "WayUp", "Freelancer", "Fiverr", "PeoplePerHour", "Toptal"]
                    if page_num == 2 and scraper_name in non_paginating_sites:
                        continue
                        
                    scraper_func = all_scrapers[scraper_name]

                    try:
                        scraped = scraper_func()
                        if scraped:
                            # Add valid, newly seen jobs to our pool for this site/role
                            for job in scraped:
                                raw_url = job.get('url', '')
                                url = normalize_url(raw_url)
                                source = job.get('source', '')
                                is_fallback = "Fallback" in source or "Search Link" in source or "Direct Link" in source or "Click to Browse All Jobs" in job.get('company', '')
                                
                                # We don't want to consider fallback generic search links as "best jobs"
                                if is_fallback:
                                    continue
                                    
                                if url and url not in seen_urls and url != '#':
                                    job['url'] = url
                                    # Always add the job; we evaluate it at the end.
                                    all_jobs_for_this_site_and_role.append(job)
                                    seen_urls.add(url)
                    except Exception as inner_e:
                        error_msg = str(inner_e)
                        print(f"    ⚠ {scraper_name} inner error on page {page_num}: {error_msg[:100]}")

                    # Small delay between pages
                    time.sleep(random.uniform(1, 2))
                
                # Now we have all jobs for this specific site and role across multiple pages.
                # We need to find the ABSOLUTE BEST one.
                if all_jobs_for_this_site_and_role:
                    print(f"    📊 Evaluated {len(all_jobs_for_this_site_and_role)} jobs from {scraper_name} for '{role}'. Finding the best one...")
                    
                    # Sort by relevance score (highest first)
                    all_jobs_for_this_site_and_role.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
                    
                    # The best job is the first one
                    best_job_for_site = all_jobs_for_this_site_and_role[0]
                    
                    # Add specific reasoning to the description
                    score = best_job_for_site.get('relevance_score', 0)
                    desc = best_job_for_site.get('description', '')
                    title = best_job_for_site.get('title', '')
                    
                    matched_skills = []
                    text_to_check = (title + " " + desc).lower()
                    for s in skills:
                        if s.lower() in text_to_check:
                            matched_skills.append(s)
                            
                    unique_matches = list(set(matched_skills))
                    
                    specific_info = f"✨ BEST MATCH ON {scraper_name.upper()} ✨\n"
                    specific_info += f"We analyzed multiple job descriptions on {scraper_name} for '{role}' and selected this as your top opportunity because it specifically requires your skills in: {', '.join(unique_matches) if unique_matches else 'the core technologies'}. "
                    
                    best_job_for_site['description'] = specific_info + "\n\nJob Details:\n" + desc
                    
                    # Add to our final list of best jobs
                    best_jobs_overall.append(best_job_for_site)
                    print(f"    ✅ Selected Best Job: {best_job_for_site['title']} at {best_job_for_site['company']} (Score: {score})")
                else:
                    print(f"    ❌ No relevant jobs found on {scraper_name} for '{role}'.")

        

    # Sort final list of best jobs by relevance score
    best_jobs_overall.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

    print(f"\n=== Total Best Jobs Found (1 per site per role): {len(best_jobs_overall)} ===")
    return best_jobs_overall
