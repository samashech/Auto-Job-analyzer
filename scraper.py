import urllib.parse
import re
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from playwright_stealth import Stealth
import time
import random

# Top Legitimate Sites Categorized
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


def calculate_relevance_score(job_title, job_description, skills):
    """
    Calculates a relevance score (0-100) based on how many user skills
    are mentioned in the job title and description.
    STRICT: Only scores high if actual technical skills are found.
    """
    if not skills:
        return 0

    text_to_check = f"{job_title} {job_description}".lower()
    skill_lower = [s.lower() for s in skills if len(s) > 2]

    if not skill_lower:
        return 0

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
    
    # Return 0 if no meaningful match found
    if matches == 0:
        return 0
    
    return score


def scrape_linkedin(page, query, skills):
    """Scrape actual job listings from LinkedIn."""
    results = []
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.linkedin.com/jobs/search/?keywords={encoded_query}"
        print(f"    [LinkedIn] Navigating to: {url}")
        page.goto(url, wait_until="networkidle", timeout=20000)
        page.wait_for_timeout(3000)  # Wait for JS to render

        soup = BeautifulSoup(page.content(), "html.parser")
        
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
    except Exception as e:
        print(f"    [LinkedIn] Scraping failed: {e}")

    return results


def scrape_indeed(page, query, skills):
    """Scrape actual job listings from Indeed."""
    results = []
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://in.indeed.com/jobs?q={encoded_query}"
        print(f"    [Indeed] Navigating to: {url}")
        page.goto(url, wait_until="networkidle", timeout=20000)
        page.wait_for_timeout(2000)

        soup = BeautifulSoup(page.content(), "html.parser")
        
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


def scrape_naukri(page, query, skills):
    """Scrape actual job listings from Naukri."""
    results = []
    try:
        dash_query = query.replace(' ', '-')
        url = f"https://www.naukri.com/{dash_query}-jobs"
        print(f"    [Naukri] Navigating to: {url}")
        page.goto(url, wait_until="networkidle", timeout=20000)
        page.wait_for_timeout(2000)

        soup = BeautifulSoup(page.content(), "html.parser")
        
        # Naukri uses dynamic class names
        job_cards = soup.find_all('article', class_=re.compile(r'jobTuple'))
        
        if not job_cards:
            job_cards = soup.find_all('div', class_=re.compile(r'jobTuple'))
        
        if not job_cards:
            job_cards = soup.find_all('a', href=re.compile(r'/job-'))
            print(f"    [Naukri] Found {len(job_cards)} jobs with fallback")
        else:
            print(f"    [Naukri] Found {len(job_cards)} jobs")

        for card in job_cards[:8]:
            try:
                title_elem = card.find('a', class_=re.compile(r'title'))
                if not title_elem:
                    title_elem = card.find('a', href=re.compile(r'/job-'))
                
                if not title_elem:
                    continue

                title = title_elem.text.strip()
                link = title_elem.get('href', '')
                if not link.startswith('http'):
                    link = f"https://www.naukri.com{link}" if link else ""

                company_elem = card.find('a', class_=re.compile(r'compName'))
                company = company_elem.text.strip() if company_elem else "Naukri Employer"

                desc_elem = card.find('p', class_=re.compile(r'desc'))
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
                
        print(f"    [Naukri] Extracted {len(results)} relevant jobs")
    except Exception as e:
        print(f"    [Naukri] Scraping failed: {e}")

    return results


def scrape_timesjobs(page, query, skills):
    """Scrape actual job listings from TimesJobs."""
    results = []
    try:
        timesjobs_query = urllib.parse.quote(query)
        timesjobs_url = f"https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords={timesjobs_query}&txtLocation="
        print(f"    [TimesJobs] Navigating to: {timesjobs_url}")
        page.goto(timesjobs_url, wait_until="networkidle", timeout=20000)
        page.wait_for_timeout(2000)

        soup = BeautifulSoup(page.content(), "html.parser")
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
    except Exception as e:
        print(f"    [TimesJobs] Scraping failed: {e}")

    return results


def scrape_internshala(page, query, skills, job_type="Full-time"):
    """Scrape actual job listings from Internshala."""
    results = []
    try:
        internshala_query = "-".join([s.lower().replace(" ", "-") for s in query.split()[:2]])
        base_path = "internships" if job_type == "Internship" else "jobs"
        scrape_url = f"https://internshala.com/{base_path}/keywords-{internshala_query}/"
        print(f"    [Internshala] Navigating to: {scrape_url}")
        page.goto(scrape_url, wait_until="networkidle", timeout=20000)
        page.wait_for_timeout(2000)

        soup = BeautifulSoup(page.content(), "html.parser")
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
    except Exception as e:
        print(f"    [Internshala] Scraping failed: {e}")

    return results


def scrape_glassdoor(page, query, skills):
    """Scrape actual job listings from Glassdoor."""
    results = []
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={encoded_query}"
        print(f"    [Glassdoor] Navigating to: {url}")
        page.goto(url, wait_until="networkidle", timeout=20000)
        page.wait_for_timeout(3000)

        soup = BeautifulSoup(page.content(), "html.parser")
        job_cards = soup.find_all('div', class_=re.compile(r'jobListing'))
        
        if not job_cards:
            job_cards = soup.find_all('li', class_=re.compile(r'JobsList'))
            print(f"    [Glassdoor] Found {len(job_cards)} jobs with fallback")
        else:
            print(f"    [Glassdoor] Found {len(job_cards)} jobs")

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
                
        print(f"    [Glassdoor] Extracted {len(results)} relevant jobs")
    except Exception as e:
        print(f"    [Glassdoor] Scraping failed: {e}")

    return results


def scrape_monster(page, query, skills):
    """Scrape actual job listings from Monster (foundit.in)."""
    results = []
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.foundit.in/srp/results?query={encoded_query}"
        print(f"    [Monster] Navigating to: {url}")
        page.goto(url, wait_until="networkidle", timeout=20000)
        page.wait_for_timeout(2000)

        soup = BeautifulSoup(page.content(), "html.parser")
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
    except Exception as e:
        print(f"    [Monster] Scraping failed: {e}")

    return results


def scrape_wellfound(page, query, skills):
    """Scrape actual job listings from Wellfound (AngelList)."""
    results = []
    try:
        dash_query = query.replace(' ', '-').lower()
        url = f"https://wellfound.com/role/l/{dash_query}"
        print(f"    [Wellfound] Navigating to: {url}")
        page.goto(url, wait_until="networkidle", timeout=20000)
        page.wait_for_timeout(2000)

        soup = BeautifulSoup(page.content(), "html.parser")
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
    except Exception as e:
        print(f"    [Wellfound] Scraping failed: {e}")

    return results


def scrape_upwork(page, query, skills):
    """Scrape actual job listings from Upwork."""
    results = []
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.upwork.com/nx/search/jobs/?q={encoded_query}"
        print(f"    [Upwork] Navigating to: {url}")
        page.goto(url, wait_until="networkidle", timeout=20000)
        page.wait_for_timeout(2000)

        soup = BeautifulSoup(page.content(), "html.parser")
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
    except Exception as e:
        print(f"    [Upwork] Scraping failed: {e}")

    return results


def get_dynamic_job_links(skills, level, job_type="Full-time"):
    """
    Dynamically scrapes actual job postings from multiple websites.
    Searches for EACH SKILL INDIVIDUALLY to maximize job results.
    """
    if not skills:
        return []

    # Clean and filter skills
    cleaned_skills = [clean_skill_for_search(s) for s in skills if len(s) > 2]
    seen = set()
    unique_skills = [x for x in cleaned_skills if not (x in seen or seen.add(x))]

    all_scraped = []
    all_seen_urls = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 720}
        )
        page = context.new_page()
        Stealth().apply_stealth_sync(page)

        # Search for EACH skill individually
        for skill_idx, skill in enumerate(unique_skills):
            print(f"\n=== Searching for skill #{skill_idx + 1}: '{skill}' ===")
            
            # Define scrapers for this skill
            scrapers = {
                "Indeed": lambda: scrape_indeed(page, skill, unique_skills),
                "LinkedIn": lambda: scrape_linkedin(page, skill, unique_skills),
                "TimesJobs": lambda: scrape_timesjobs(page, skill, unique_skills),
                "Naukri": lambda: scrape_naukri(page, skill, unique_skills),
                "Internshala": lambda: scrape_internshala(page, skill, unique_skills, job_type),
                "Glassdoor": lambda: scrape_glassdoor(page, skill, unique_skills),
                "Monster": lambda: scrape_monster(page, skill, unique_skills),
                "Wellfound": lambda: scrape_wellfound(page, skill, unique_skills),
                "Upwork": lambda: scrape_upwork(page, skill, unique_skills) if job_type == "Freelance" else []
            }

            # Try each scraper for this skill
            for scraper_name, scraper_func in scrapers.items():
                try:
                    print(f"  Scraping {scraper_name} for '{skill}'...")
                    scraped = scraper_func()
                    
                    if scraped:
                        # Filter out duplicates and jobs with 0 relevance
                        for job in scraped:
                            url = job.get('url', '')
                            if url and url not in all_seen_urls and url != '#' and job.get('relevance_score', 0) > 0:
                                all_seen_urls.add(url)
                                all_scraped.append(job)
                        
                        print(f"    -> Got {len(scraped)} jobs ({len([j for j in scraped if j.get('relevance_score', 0) > 0])} relevant)")
                    else:
                        print(f"    -> No jobs found")

                    # Small delay between requests to avoid detection
                    time.sleep(random.uniform(1.5, 3))

                except Exception as e:
                    print(f"    -> {scraper_name} failed: {e}")
                    continue
            
            # If we have enough jobs, we can stop searching
            if len(all_scraped) >= 30:
                print(f"\n✓ Found {len(all_scraped)} jobs, stopping early")
                break

        browser.close()

    # Sort by relevance score (highest first)
    all_scraped.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

    print(f"\n=== Total jobs found: {len(all_scraped)} ===")
    return all_scraped[:30]
