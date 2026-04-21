from scraper import get_dynamic_job_links
from pprint import pprint

jobs = get_dynamic_job_links(["Python", "Flask", "React"], "Experienced", "Full-time", "Senior", "Remote")
print(f"Total returned: {len(jobs)}")
for j in jobs:
    print(f"{j['name']}: {j['title']} - Score: {j.get('relevance_score')}")
