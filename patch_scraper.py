import re

with open('/home/samash/Documents/Project RAIoT/scraper.py', 'r') as f:
    content = f.read()

# Update get_dynamic_job_links signature and logic
old_def = 'def get_dynamic_job_links(skills, level, job_type="Full-time", experience_level="", location=""):\\n    """\\n    Dynamically scrapes actual job postings from multiple websites.\\n    Searches for EACH SKILL INDIVIDUALLY to maximize job results.'
new_def = 'def get_dynamic_job_links(skills, level, job_type="Full-time", experience_level="", location="", job_role=""):\\n    """\\n    Dynamically scrapes actual job postings from multiple websites.\\n    Searches for JOB ROLE and scrapes multiple pages.'
content = content.replace(old_def, new_def)

# Update the loop to use job_role and page_num
old_loop = """    # Clean and filter skills
    cleaned_skills = [clean_skill_for_search(s) for s in skills if len(s) > 2]
    seen = set()
    unique_skills = [x for x in cleaned_skills if not (x in seen or seen.add(x))]

    # Limit to top 5 skills to significantly improve speed
    if len(unique_skills) > 5:
        print(f"\\n⚠ Limiting to top 5 skills (had {len(unique_skills)}) to avoid timeout")
        unique_skills = unique_skills[:5]"""

new_loop = """    if not job_role:
        from analyzer import infer_job_role
        job_role = infer_job_role(skills)

    unique_skills = [job_role]"""
content = content.replace(old_loop, new_loop)

# Let's fix the calls to the scrapers to pass page_num
old_calls = """            # Define ALL possible scrapers
            all_scrapers = {
                "Indeed": lambda: scrape_indeed(page, skill, unique_skills, experience_level or level, location),
                "LinkedIn": lambda: scrape_linkedin(page, skill, unique_skills, experience_level or level, location),
                "TimesJobs": lambda: scrape_timesjobs(page, skill, unique_skills, experience_level or level, location),
                "Naukri": lambda: scrape_naukri(page, skill, unique_skills, experience_level or level, location),
                "Internshala": lambda: scrape_internshala(page, skill, unique_skills, job_type, experience_level or level),
                "Glassdoor": lambda: scrape_glassdoor(page, skill, unique_skills, experience_level or level, location),
                "Monster": lambda: scrape_monster(page, skill, unique_skills, experience_level or level, location),
                "Wellfound": lambda: scrape_wellfound(page, skill, unique_skills, experience_level or level),
                "Upwork": lambda: scrape_upwork(page, skill, unique_skills),
                "Dice": lambda: scrape_dice(page, skill, unique_skills, location),
                "WeWorkRemotely": lambda: scrape_weworkremotely(page, skill, unique_skills),
                "FlexJobs": lambda: scrape_flexjobs(page, skill, unique_skills, experience_level or level, location),
                "Apna": lambda: scrape_apna(page, skill, unique_skills, experience_level or level, location),
                "Snagajob": lambda: scrape_snagajob(page, skill, unique_skills, experience_level or level, location),
                "Unstop": lambda: scrape_unstop(page, skill, unique_skills, job_type, experience_level or level),
                "WayUp": lambda: scrape_wayup(page, skill, unique_skills, job_type, experience_level or level),
                "Freelancer": lambda: scrape_freelancer(page, skill, unique_skills, experience_level or level, location),
                "Fiverr": lambda: scrape_fiverr(page, skill, unique_skills, experience_level or level, location),
                "PeoplePerHour": lambda: scrape_peopleperhour(page, skill, unique_skills, experience_level or level, location),
                "Toptal": lambda: scrape_toptal(page, skill, unique_skills, experience_level or level, location),
            }"""

new_calls = """            # Define ALL possible scrapers
            all_scrapers = {
                "Indeed": lambda: scrape_indeed(page, skill, skills, experience_level or level, location, page_num),
                "LinkedIn": lambda: scrape_linkedin(page, skill, skills, experience_level or level, location, page_num),
                "TimesJobs": lambda: scrape_timesjobs(page, skill, skills, experience_level or level, location),
                "Naukri": lambda: scrape_naukri(page, skill, skills, experience_level or level, location, page_num),
                "Internshala": lambda: scrape_internshala(page, skill, skills, job_type, experience_level or level),
                "Glassdoor": lambda: scrape_glassdoor(page, skill, skills, experience_level or level, location, page_num),
                "Monster": lambda: scrape_monster(page, skill, skills, experience_level or level, location),
                "Wellfound": lambda: scrape_wellfound(page, skill, skills, experience_level or level),
                "Upwork": lambda: scrape_upwork(page, skill, skills),
                "Dice": lambda: scrape_dice(page, skill, skills, location),
                "WeWorkRemotely": lambda: scrape_weworkremotely(page, skill, skills),
                "FlexJobs": lambda: scrape_flexjobs(page, skill, skills, experience_level or level, location),
                "Apna": lambda: scrape_apna(page, skill, skills, experience_level or level, location),
                "Snagajob": lambda: scrape_snagajob(page, skill, skills, experience_level or level, location),
                "Unstop": lambda: scrape_unstop(page, skill, skills, job_type, experience_level or level),
                "WayUp": lambda: scrape_wayup(page, skill, skills, job_type, experience_level or level),
                "Freelancer": lambda: scrape_freelancer(page, skill, skills, experience_level or level, location),
                "Fiverr": lambda: scrape_fiverr(page, skill, skills, experience_level or level, location),
                "PeoplePerHour": lambda: scrape_peopleperhour(page, skill, skills, experience_level or level, location),
                "Toptal": lambda: scrape_toptal(page, skill, skills, experience_level or level, location),
            }"""
content = content.replace(old_calls, new_calls)

# Modify the loop to include page_num
old_search_loop = """        # Search for EACH skill individually
        for skill_idx, skill in enumerate(unique_skills):
            print(f"\\n=== Searching for skill #{skill_idx + 1}/{len(unique_skills)}: '{skill}' ===")
            print(f"    Experience: {experience_level or level}, Location: {location or 'Any'}")"""

new_search_loop = """        # Search for Job Role over 2 pages
        for page_num in [1, 2]:
            skill = job_role
            print(f"\\n=== Searching for role: '{skill}', Page: {page_num} ===")
            print(f"    Experience: {experience_level or level}, Location: {location or 'Any'}")"""
content = content.replace(old_search_loop, new_search_loop)


# Add page_num to the definitions of top 4 scrapers
# 1. LinkedIn
content = content.replace('def scrape_linkedin(page, query, skills, experience_level="", location=""):', 'def scrape_linkedin(page, query, skills, experience_level="", location="", page_num=1):')
content = content.replace('url = f"https://www.linkedin.com/jobs/search/?keywords={encoded_query}"', 'url = f"https://www.linkedin.com/jobs/search/?keywords={encoded_query}" + (f"&start={(page_num-1)*25}" if page_num > 1 else "")')

# 2. Indeed
content = content.replace('def scrape_indeed(page, query, skills, experience_level="", location=""):', 'def scrape_indeed(page, query, skills, experience_level="", location="", page_num=1):')
content = content.replace('url = f"https://in.indeed.com/jobs?q={encoded_query}"', 'url = f"https://in.indeed.com/jobs?q={encoded_query}" + (f"&start={(page_num-1)*10}" if page_num > 1 else "")')

# 3. Naukri
content = content.replace('def scrape_naukri(page, query, skills, experience_level="", location=""):', 'def scrape_naukri(page, query, skills, experience_level="", location="", page_num=1):')
content = content.replace('url = f"https://www.naukri.com/naukri/search/results?keyword={urllib.parse.quote(job_role)}"', 'url = f"https://www.naukri.com/naukri/search/results?keyword={urllib.parse.quote(job_role)}" + (f"&pageNo={page_num}" if page_num > 1 else "")')

# 4. Glassdoor
content = content.replace('def scrape_glassdoor(page, query, skills, experience_level="", location=""):', 'def scrape_glassdoor(page, query, skills, experience_level="", location="", page_num=1):')
content = content.replace('url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={encoded_query}"', 'url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={encoded_query}" + (f"&p={page_num}" if page_num > 1 else "")')

with open('/home/samash/Documents/Project RAIoT/scraper.py', 'w') as f:
    f.write(content)

