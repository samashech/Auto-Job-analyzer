from scraper import scrape_jobs
from analyzer import extract_skills, calculate_match_score
from visualizer import generate_chart
# from notifier import send_telegram_alert

# Your current real-world skills
MY_PROFILE_SKILLS = ["python", "sql", "git", "pandas", "machine learning"]

def run_pipeline():
    print("1. Starting Web Scraper...")
    job_data = scrape_jobs("AI Engineer", "Jaipur")
    
    print("2. Analyzing Job Descriptions...")
    skill_frequencies = extract_skills(job_data)
    
    print("3. Calculating Match Score...")
    match_score = calculate_match_score(skill_frequencies, MY_PROFILE_SKILLS)
    
    print("4. Generating Visualization...")
    chart_filename = generate_chart(skill_frequencies)
    
    print("5. Generating Summary...")
    summary_message = (
        f"📊 Weekly Job Market Update!\n\n"
        f"Role: AI Engineer\n"
        f"Your Profile Match Score: {match_score}%\n\n"
        f"See the attached chart for the top required skills."
    )
    
    # send_telegram_alert(summary_message, chart_filename)
    
    print("Pipeline Complete! Check your local directory for the chart.")

if __name__ == "__main__":
    run_pipeline()
