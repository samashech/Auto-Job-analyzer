import urllib.parse
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from playwright_stealth import stealth
import time
import random

# Top 10 Legitimate Sites Categorized
LEGIT_SITES = {
    "Full-time": [
        {"name": "LinkedIn", "base": "https://www.linkedin.com/jobs/search/?keywords={query}"},
        {"name": "Indeed", "base": "https://in.indeed.com/jobs?q={query}"},
        {"name": "Glassdoor", "base": "https://www.glassdoor.com/Job/jobs.htm?sc.keyword={query}"},
        {"name": "Wellfound", "base": "https://wellfound.com/role/l/{dash_query}"},
        {"name": "Naukri", "base": "https://www.naukri.com/{dash_query}-jobs"},
        {"name": "ZipRecruiter", "base": "https://www.ziprecruiter.in/jobs/search?q={query}"},
        {"name": "Monster", "base": "https://www.foundit.in/srp/results?query={query}"},
        {"name": "SimplyHired", "base": "https://www.simplyhired.co.in/search?q={query}"},
        {"name": "Dice", "base": "https://www.dice.com/jobs?q={query}"},
        {"name": "CareerBuilder", "base": "https://www.careerbuilder.com/jobs?keywords={query}"}
    ],
    "Part-time": [
        {"name": "LinkedIn Part-Time", "base": "https://www.linkedin.com/jobs/search/?keywords={query}%20Part%20Time"},
        {"name": "Indeed Part-Time", "base": "https://in.indeed.com/jobs?q={query}+part+time"},
        {"name": "FlexJobs", "base": "https://www.flexjobs.com/search?search={query}&schedule=Part-Time"},
        {"name": "Glassdoor Part-Time", "base": "https://www.glassdoor.com/Job/jobs.htm?sc.keyword={query}%20part%20time"},
        {"name": "Snagajob", "base": "https://www.snagajob.com/search?q={query}"},
        {"name": "SimplyHired", "base": "https://www.simplyhired.co.in/search?q={query}+part+time"},
        {"name": "ZipRecruiter", "base": "https://www.ziprecruiter.in/jobs/search?q={query}+part+time"},
        {"name": "Wellfound", "base": "https://wellfound.com/role/l/{dash_query}-part-time"},
        {"name": "Upwork (Hourly)", "base": "https://www.upwork.com/nx/search/jobs/?q={query}"},
        {"name": "Fiverr", "base": "https://www.fiverr.com/search/gigs?query={query}"}
    ],
    "Internship": [
        {"name": "Internshala", "base": "https://internshala.com/internships/keywords-{dash_query}/"},
        {"name": "LinkedIn Internships", "base": "https://www.linkedin.com/jobs/search/?keywords={query}%20Internship"},
        {"name": "WayUp", "base": "https://www.wayup.com/s/internships/{dash_query}/"},
        {"name": "Glassdoor Interns", "base": "https://www.glassdoor.com/Job/jobs.htm?sc.keyword={query}%20internship"},
        {"name": "Indeed Interns", "base": "https://in.indeed.com/jobs?q={query}+internship"},
        {"name": "Chegg Internships", "base": "https://www.internships.com/search?q={query}"},
        {"name": "Handshake", "base": "https://app.joinhandshake.com/stu/postings?query={query}"},
        {"name": "LetsIntern", "base": "https://www.letsintern.com/internships?q={query}"},
        {"name": "Wellfound Interns", "base": "https://wellfound.com/role/l/{dash_query}-internship"},
        {"name": "Naukri Interns", "base": "https://www.naukri.com/{dash_query}-internship-jobs"}
    ],
    "Freelance": [
        {"name": "Upwork", "base": "https://www.upwork.com/nx/search/jobs/?q={query}"},
        {"name": "Freelancer", "base": "https://www.freelancer.com/jobs/?keyword={query}"},
        {"name": "Fiverr", "base": "https://www.fiverr.com/search/gigs?query={query}"},
        {"name": "Toptal", "base": "https://www.toptal.com/talent/apply"},
        {"name": "Guru", "base": "https://www.guru.com/d/jobs/q/{query}/"},
        {"name": "PeoplePerHour", "base": "https://www.peopleperhour.com/freelance-jobs?q={query}"},
        {"name": "FlexJobs", "base": "https://www.flexjobs.com/search?search={query}&jobType=Freelance"},
        {"name": "SolidGigs", "base": "https://solidgigs.com/"},
        {"name": "WeWorkRemotely", "base": "https://weworkremotely.com/remote-jobs/search?term={query}"},
        {"name": "Hubstaff Talent", "base": "https://talent.hubstaff.com/search/jobs?search={query}"}
    ]
}

def get_dynamic_job_links(skills, level, job_type="Full-time"):
    """
    Combines Playwright stealth scraping (to get actual specific latest job postings)
    with top 10 dynamic search URLs for the user's top 10 skills.
    """
    # The system matches the current user's top 10 skills
    top_skills = skills[:10] if skills else ["Developer"]
    query = " ".join(top_skills)
    
    encoded_query = urllib.parse.quote(query)
    dash_query = query.replace(' ', '-').replace('/', '-')
    
    results = []
    
    # 1. Attempt to stealth scrape actual specific latest jobs from a generic board 
    # Using Playwright & BeautifulSoup
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            stealth_sync(page)
            
            # Example scraping from an open remote board (WeWorkRemotely) as it's less hostile to scraping
            scrape_url = f"https://weworkremotely.com/remote-jobs/search?term={encoded_query}"
            page.goto(scrape_url, timeout=15000)
            # Wait for jobs to load
            time.sleep(2) 
            html = page.content()
            soup = BeautifulSoup(html, "html.parser")
            
            job_cards = soup.find_all("li", class_="feature")
            for card in job_cards[:3]: # Get top 3 latest scraped jobs
                title_elem = card.find("span", class_="title")
                company_elem = card.find("span", class_="company")
                link_elem = card.find("a")
                
                if title_elem and link_elem:
                    title = title_elem.text.strip()
                    company = company_elem.text.strip() if company_elem else "Unknown Company"
                    link = "https://weworkremotely.com" + link_elem["href"]
                    
                    results.append({
                        "name": "WeWorkRemotely (Scraped)",
                        "title": title,
                        "company": company,
                        "url": link,
                        "description": f"Actual recent posting scraped for your top skills: {', '.join(top_skills[:3])}."
                    })
            browser.close()
    except Exception as e:
        print(f"Playwright scraping failed/skipped: {e}")
        
    # 2. Append the Top 10 legitimate job boards matching the exact Job Type
    # This ensures the user gets exact links to all applicable roles separated by their requested type.
    category_sites = LEGIT_SITES.get(job_type, LEGIT_SITES["Full-time"])
    
    for site in category_sites:
        url = site["base"].format(query=encoded_query, dash_query=dash_query)
        results.append({
            "name": site["name"],
            "title": f"{job_type} Role - {site['name']}",
            "company": "Various Companies",
            "url": url,
            "description": f"Top 10 matched {job_type} opportunities for your top 10 skills: {', '.join(top_skills)}."
        })
        
    return results
