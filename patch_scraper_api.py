import re

def refactor_scraper():
    with open("scraper.py", "r") as f:
        content = f.read()

    # 1. Add SCRAPER_API_KEY and fetch_html function at the top
    api_key_code = """
SCRAPER_API_KEY = "75b720c9b40e84cae7d19b655ac80746"

def fetch_html(url, render=False, premium=False):
    import requests
    payload = {
        'api_key': SCRAPER_API_KEY,
        'url': url,
        'render': 'true' if render else 'false',
        'premium': 'true' if premium else 'false'
    }
    try:
        print(f"    [ScraperAPI] Fetching: {url} (render={render}, premium={premium})")
        res = requests.get('https://api.scraperapi.com/', params=payload, timeout=60)
        if res.status_code == 200:
            return res.text
        else:
            print(f"    [ScraperAPI] Error {res.status_code}: {res.text[:100]}")
    except Exception as e:
        print(f"    [ScraperAPI] Request failed: {e}")
    return ""
"""
    if "SCRAPER_API_KEY" not in content:
        content = content.replace("import requests", "import requests\n" + api_key_code)

    # 2. Update function signatures
    # Change def scrape_xxx(page, query...) to def scrape_xxx(query...)
    content = re.sub(r'def scrape_([a-z]+)\(page, ', r'def scrape_\1(', content)

    # 3. Replace page.goto, page.wait_for_timeout, page.content() with fetch_html
    # We will find blocks like:
    # page.goto(url, wait_until="domcontentloaded", timeout=25000)
    # page.wait_for_timeout(2000)
    # ...
    # soup = BeautifulSoup(page.content(), "html.parser")
    
    # Let's just do a generic replacement for the common patterns:
    
    content = re.sub(r'page\.goto\([^)]+\)', '', content)
    content = re.sub(r'page\.wait_for_timeout\([^)]+\)', '', content)
    
    # We need to assign `html = fetch_html(url, render=True, premium=True)`
    # The URL variable is usually `url`. We'll just replace `BeautifulSoup(page.content(), "html.parser")`
    # with `html = fetch_html(url, render=True, premium=True); soup = BeautifulSoup(html, "html.parser")`
    
    # Sometimes it's `if _is_blocked(page.content()):`
    # Let's first replace `page.content()` with `html_content`
    # and insert `html_content = fetch_html(url, render=True, premium=True)` right before it's used.
    
    def replacer(match):
        return f"html_content = fetch_html(url, render=True, premium=True)\n        {match.group(1)}html_content{match.group(2)}"
    
    # A bit risky. Let's be more precise.
    # We'll just replace `if _is_blocked(page.content()):` with `html_content = fetch_html(url, render=True, premium=True)\n        if _is_blocked(html_content):`
    content = content.replace('if _is_blocked(page.content()):', 
                              'html_content = fetch_html(url, render=True, premium=True)\n        if _is_blocked(html_content):')
                              
    # And replace `BeautifulSoup(page.content(), "html.parser")` with `BeautifulSoup(html_content, "html.parser")`
    # Wait, some scrapers don't check `_is_blocked`.
    # Let's replace `BeautifulSoup(page.content(), "html.parser")` with:
    # `html_content = fetch_html(url, render=True, premium=True) if 'html_content' not in locals() else html_content\n        soup = BeautifulSoup(html_content, "html.parser")`
    content = content.replace('soup = BeautifulSoup(page.content(), "html.parser")',
                              "if 'html_content' not in locals():\n            html_content = fetch_html(url, render=True, premium=True)\n        soup = BeautifulSoup(html_content, \"html.parser\")")

    # 4. In get_dynamic_job_links:
    # Remove Playwright block
    
    playwright_start = content.find("with sync_playwright() as p:")
    if playwright_start != -1:
        # We need to unindent everything inside the playwright block and remove the playwright setup
        # It's easier to just replace `with sync_playwright() as p:` with `if True:`
        # and remove browser setup
        
        # Replace the `with sync_playwright() as p:` block:
        content = content.replace("with sync_playwright() as p:", "if True:")
        
        # We also need to remove the browser launching code:
        content = re.sub(r'browser = p\.chromium\.launch\([^)]+\)', 'browser = None', content)
        content = re.sub(r'context = browser\.new_context\([^)]+\)', 'context = None', content)
        content = re.sub(r'page = context\.new_page\(\)', 'page = None', content)
        content = re.sub(r'Stealth\(\)\.apply_stealth_sync\(page\)', '', content)
        content = re.sub(r'page\.set_default_timeout\([^)]+\)', '', content)
        
        content = content.replace("browser.close()", "")
    
    # 5. Fix the dictionary in get_dynamic_job_links to not pass `page`
    content = re.sub(r'lambda: scrape_([a-z]+)\(page, ', r'lambda: scrape_\1(', content)

    with open("scraper_new.py", "w") as f:
        f.write(content)

refactor_scraper()
