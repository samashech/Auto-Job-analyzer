import urllib.parse
import re

def modify_scraper():
    with open("scraper.py", "r") as f:
        content = f.read()

    # Define the correctly formatted function
    new_get_dynamic_job_links = r"""def get_dynamic_job_links(skills, level, job_type="Full-time", experience_level="", location="", job_role=""):
    """
    Dynamically scrapes actual job postings from multiple websites.
    Searches for EACH JOB ROLE INDIVIDUALLY to maximize job results.
    Uses experience level and location for better targeting.
    Filters heavily based on user's actual skills to find the best match per site.
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

    # Define sites that actually work with ScraperAPI Free Tier
    all_possible_sites = [
        "Freelancer", "PeoplePerHour", "Toptal", "Unstop", "WayUp"
    ]
    
    # Remove duplicates but keep a consistent order
    sites_to_scrape = list(dict.fromkeys(all_possible_sites))
    
    print(f"\n🎯 Job Type: {job_type}")
    print(f"📋 Roles to Search: {', '.join(roles_to_search)}")
    print(f"📋 Scraping {len(sites_to_scrape)} sites: {', '.join(sites_to_scrape)}")

    best_jobs_overall = []
    seen_urls = set()

    if True:
        page = ScraperAPIPage()

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
                        "TimesJobs": lambda: scrape_timesjobs(role, skills, experience_level or level, location),
                        "Naukri": lambda: scrape_naukri(role, skills, experience_level or level, location, page_num),
                        "Internshala": lambda: scrape_internshala(role, skills, job_type, experience_level or level),
                        "Glassdoor": lambda: scrape_glassdoor(role, skills, experience_level or level, location, page_num),
                        "Monster": lambda: scrape_monster(role, skills, experience_level or level, location),
                        "Wellfound": lambda: scrape_wellfound(role, skills, experience_level or level),
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

        pass

    # Sort final list of best jobs by relevance score
    best_jobs_overall.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

    print(f"\n=== Total Best Jobs Found (1 per site per role): {len(best_jobs_overall)} ===")
    return best_jobs_overall"""

    # We will use regex to replace everything from def get_dynamic_job_links to the end of file
    import re
    # Escape special regex characters in the search pattern if necessary, but here we can just use a simple string match
    start_tag = 'def get_dynamic_job_links(skills, level, job_type="Full-time", experience_level="", location=""):'
    start_idx = content.find(start_tag)
    if start_idx != -1:
        content = content[:start_idx] + new_get_dynamic_job_links
    else:
        # Try finding with any variations or just roles
        content = re.sub(r'def get_dynamic_job_links\(.*', new_get_dynamic_job_links, content, flags=re.DOTALL)
    
    with open("scraper.py", "w") as f:
        f.write(content)

modify_scraper()
