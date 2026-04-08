from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import time
import random

def scrape_jobs(search_term: str, location: str) -> list:
    """Scrapes job descriptions using advanced stealth and direct URL navigation."""
    scraped_data = []
    
    with sync_playwright() as p:
        # TACTIC 1: Disable the blink automation feature (CRITICAL)
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"] 
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = context.new_page()
        stealth_sync(page)
        
        # Build the URL based on your parameters
        base_url = f"https://in.indeed.com/jobs?q={search_term.replace(' ', '+')}&l={location.replace(' ', '+')}"
        
        print(f"Navigating to {base_url}...")
        page.goto(base_url)
        
        # TACTIC 2: Wait like a human before looking for elements
        time.sleep(random.uniform(3.0, 5.0))
        
        try:
            page.wait_for_selector(".job_seen_beacon", timeout=15000)
            job_cards = page.locator(".job_seen_beacon").all()
            print(f"Found {len(job_cards)} jobs on this page.")
            
            job_urls = []
            
            print("Extracting job links...")
            for card in job_cards[:3]: # Limit to 3 for testing to avoid immediate bans
                title_element = card.locator(".jcs-JobTitle")
                title = title_element.inner_text()
                company = card.locator('[data-testid="company-name"]').inner_text()
                
                partial_url = title_element.get_attribute("href")
                # Handle cases where Indeed uses relative vs absolute URLs
                if partial_url.startswith("http"):
                    full_url = partial_url
                else:
                    full_url = f"https://in.indeed.com{partial_url}"
                
                job_urls.append({
                    "title": title,
                    "company": company,
                    "url": full_url
                })
                
            print("Visiting individual job pages to get descriptions...")
            for job in job_urls:
                print(f"Scraping: {job['title']} at {job['company']}")
                
                # Navigate to the specific job page
                page.goto(job['url'])
                
                # Wait for the description to load
                page.wait_for_selector("#jobDescriptionText", timeout=10000)
                description = page.locator("#jobDescriptionText").inner_text()
                
                job["description"] = description
                scraped_data.append(job)
                
                # TACTIC 3: Crucial delay between visiting job pages
                time.sleep(random.uniform(4.0, 8.0)) 
                
        except Exception as e:
            print(f"An error occurred (possibly blocked): {e}")
            
        finally:
            browser.close()
            
    return scraped_data

if __name__ == "__main__":
    # Test with your specific search
    data = scrape_jobs("AI Engineer", "Jaipur, Rajasthan")
    print(f"\nSuccessfully scraped {len(data)} job descriptions.")
