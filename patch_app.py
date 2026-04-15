import os
import re

with open('app.py', 'r') as f:
    content = f.read()

# Add CORS import
if 'from flask_cors import CORS' not in content:
    content = content.replace('from flask import Flask', 'from flask import Flask\nfrom flask_cors import CORS')

# Initialize CORS
if 'CORS(app' not in content:
    content = content.replace('app = Flask(__name__)', 'app = Flask(__name__)\nCORS(app, supports_credentials=True)')

# Add DB Migrations for extended profile and job fields
migration_code = """
        try:
            cursor.execute("ALTER TABLE user ADD COLUMN about TEXT")
            cursor.execute("ALTER TABLE user ADD COLUMN projects TEXT")
            cursor.execute("ALTER TABLE user ADD COLUMN achievements TEXT")
            cursor.execute("ALTER TABLE user ADD COLUMN education TEXT")
            cursor.execute("ALTER TABLE user ADD COLUMN certificates TEXT")
            cursor.execute("ALTER TABLE user ADD COLUMN positions_of_responsibility TEXT")
            cursor.execute("ALTER TABLE user ADD COLUMN social_github VARCHAR(256)")
            cursor.execute("ALTER TABLE user ADD COLUMN social_linkedin VARCHAR(256)")
            cursor.execute("ALTER TABLE user ADD COLUMN social_portfolio VARCHAR(256)")
            cursor.execute("ALTER TABLE user ADD COLUMN photo_data_url TEXT")
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute("ALTER TABLE job_match ADD COLUMN salary VARCHAR(100)")
            cursor.execute("ALTER TABLE job_match ADD COLUMN location VARCHAR(250)")
            cursor.execute("ALTER TABLE job_match ADD COLUMN skills_required TEXT")
            cursor.execute("ALTER TABLE job_match ADD COLUMN region VARCHAR(50)")
            cursor.execute("ALTER TABLE job_match ADD COLUMN state_or_continent VARCHAR(100)")
        except sqlite3.OperationalError:
            pass
"""

if 'ALTER TABLE user ADD COLUMN about TEXT' not in content:
    content = content.replace('conn.commit()\n        conn.close()', migration_code + '\n        conn.commit()\n        conn.close()')


# Update background_scrape_job saving part
# We need to map scraper response to the new JobMatch fields.
background_scrape_old = """                new_match = JobMatch(
                    user_id=user_id,
                    title=job.get('title', f"{level} Role"),
                    company=job.get('company', 'Various Companies'),
                    url=job.get('url', '#'),
                    source=job.get('name', job.get('source', 'Web Scraper')),
                    job_type=job_type,
                    relevance_score=job.get('relevance_score', 0)
                )"""

background_scrape_new = """                new_match = JobMatch(
                    user_id=user_id,
                    title=job.get('title', f"{level} Role"),
                    company=job.get('company', 'Various Companies'),
                    url=job.get('url', '#'),
                    source=job.get('name', job.get('source', 'Web Scraper')),
                    job_type=job_type,
                    relevance_score=job.get('relevance_score', 0),
                    salary=job.get('salary', 'Not specified'),
                    location=job.get('location', 'Remote'),
                    skills_required=','.join(job.get('skills', [])) if isinstance(job.get('skills'), list) else str(job.get('skills', '')),
                    region=job.get('region', 'India'),
                    state_or_continent=job.get('stateOrContinent', 'All')
                )"""
if background_scrape_old in content:
    content = content.replace(background_scrape_old, background_scrape_new)

# Modify user returned in login
user_response_old = """        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'skills': user.skills,
            'level': user.level,
            'location': user.location,
            'job_type': user.job_type,
            'job_role': user.job_role,
            'resume_url': user.resume_url,
            'has_resume_data': has_resume_data,
            'profile_complete': profile_complete,
            'existing_jobs_count': existing_jobs_count
        }"""
user_response_new = """        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'skills': user.skills,
            'level': user.level,
            'location': user.location,
            'job_type': user.job_type,
            'job_role': user.job_role,
            'resume_url': user.resume_url,
            'about': user.about,
            'projects': user.projects,
            'achievements': user.achievements,
            'education': user.education,
            'certificates': user.certificates,
            'positions_of_responsibility': user.positions_of_responsibility,
            'social_github': user.social_github,
            'social_linkedin': user.social_linkedin,
            'social_portfolio': user.social_portfolio,
            'photo_data_url': user.photo_data_url,
            'has_resume_data': has_resume_data,
            'profile_complete': profile_complete,
            'existing_jobs_count': existing_jobs_count
        }"""
if user_response_old in content:
    content = content.replace(user_response_old, user_response_new)


# Modify user returned in check_session
check_session_old = """                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'skills': user.skills,
                    'level': user.level,
                    'location': user.location,
                    'job_type': user.job_type,
                    'job_role': user.job_role,
                    'resume_url': user.resume_url,
                    'has_resume_data': bool(user.skills and user.level),
                    'profile_complete': profile_complete
                }"""
check_session_new = """                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'skills': user.skills,
                    'level': user.level,
                    'location': user.location,
                    'job_type': user.job_type,
                    'job_role': user.job_role,
                    'resume_url': user.resume_url,
                    'about': user.about,
                    'projects': user.projects,
                    'achievements': user.achievements,
                    'education': user.education,
                    'certificates': user.certificates,
                    'positions_of_responsibility': user.positions_of_responsibility,
                    'social_github': user.social_github,
                    'social_linkedin': user.social_linkedin,
                    'social_portfolio': user.social_portfolio,
                    'photo_data_url': user.photo_data_url,
                    'has_resume_data': bool(user.skills and user.level),
                    'profile_complete': profile_complete
                }"""
if check_session_old in content:
    content = content.replace(check_session_old, check_session_new)

# Modify update profile preferences
update_profile_pref_code = """
    if 'skills' in data:
        user.skills = data['skills']
        
    if 'about' in data: user.about = data['about']
    if 'projects' in data: user.projects = data['projects']
    if 'achievements' in data: user.achievements = data['achievements']
    if 'education' in data: user.education = data['education']
    if 'certificates' in data: user.certificates = data['certificates']
    if 'positions_of_responsibility' in data: user.positions_of_responsibility = data['positions_of_responsibility']
    
    if 'social' in data and data['social']:
        social = data['social']
        if 'github' in social: user.social_github = social['github']
        if 'linkedIn' in social: user.social_linkedin = social['linkedIn']
        if 'portfolio' in social: user.social_portfolio = social['portfolio']
        
    if 'photoDataUrl' in data: user.photo_data_url = data['photoDataUrl']
"""

if 'if \'about\' in data:' not in content:
    content = content.replace("    if 'skills' in data:\n        user.skills = data['skills']", update_profile_pref_code)

# Add extended job mapping for get_jobs, api_all_jobs, and api_saved_jobs
job_dict_old = """    jobs_data = [{
        'id': job.id,
        'title': job.title,
        'company': job.company,
        'url': job.url,
        'source': job.source,
        'job_type': job.job_type,
        'relevance_score': job.relevance_score
    } for job in jobs]"""
job_dict_new = """    jobs_data = [{
        'id': job.id,
        'title': job.title,
        'company': job.company,
        'url': job.url,
        'source': job.source,
        'job_type': job.job_type,
        'relevance_score': job.relevance_score,
        'salary': job.salary or 'Not specified',
        'location': job.location or 'Remote',
        'skills': [s.strip() for s in job.skills_required.split(',')] if job.skills_required else [],
        'region': job.region or 'India',
        'stateOrContinent': job.state_or_continent or 'All',
        'type': [job.job_type] if job.job_type else ['Full Time']
    } for job in jobs]"""
if job_dict_old in content:
    content = content.replace(job_dict_old, job_dict_new)

# Similarly for jobs with 'saved': job.saved
job_dict_saved_old = """    jobs_data = [{
        'id': job.id,
        'title': job.title,
        'company': job.company,
        'url': job.url,
        'source': job.source,
        'job_type': job.job_type,
        'relevance_score': job.relevance_score,
        'saved': job.saved
    } for job in jobs]"""
job_dict_saved_new = """    jobs_data = [{
        'id': job.id,
        'title': job.title,
        'company': job.company,
        'url': job.url,
        'source': job.source,
        'job_type': job.job_type,
        'relevance_score': job.relevance_score,
        'saved': job.saved,
        'salary': job.salary or 'Not specified',
        'location': job.location or 'Remote',
        'skills': [s.strip() for s in job.skills_required.split(',')] if job.skills_required else [],
        'region': job.region or 'India',
        'stateOrContinent': job.state_or_continent or 'All',
        'type': [job.job_type] if job.job_type else ['Full Time']
    } for job in jobs]"""
if job_dict_saved_old in content:
    content = content.replace(job_dict_saved_old, job_dict_saved_new)

with open('app.py', 'w') as f:
    f.write(content)

print("App patched successfully!")
