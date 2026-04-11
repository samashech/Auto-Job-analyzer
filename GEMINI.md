# Project RAIoT - Analysis & Future Implementation Plan

## 1. Current Project State & Architecture
**RAIoT (Resume Analysis & Intelligent Opportunity Tracking)** is currently a Flask-based web application designed to match a candidate's resume with job market opportunities. 

### Core Components Analyzed:
- **Web App (`app.py`)**: A Flask backend that handles routes for the dashboard (`index.html`), mock authentication, resume uploading, job fetching, and application tracking. It uses Flask `session` to temporarily store extracted skills and user level.
- **Resume Parsing (`analyzer.py`)**: Uses `PyPDF2` to extract text from a PDF resume. It employs a rudimentary regex matching system against a hardcoded list of 9 technologies (python, aws, docker, etc.) and uses basic keyword matching to determine if a candidate is a "Fresher" or "Experienced".
- **Job 'Scraping' (`scraper.py`)**: Currently acts as a URL generator rather than an actual scraper. It takes the candidate's primary skill and level and constructs search URLs for platforms like Indeed, LinkedIn, Glassdoor, Wellfound, and Naukri.
- **Visualization (`visualizer.py`)**: Utilizes `matplotlib`, `seaborn`, and `pandas` to generate a bar chart (`trend_chart.png`) of the user's skills against dummy "Demand Scores". This chart is saved statically and served to the frontend.
- **Notifications (`notifier.py`)**: A standalone script ready to send text and images via the Telegram API, though currently requiring manual configuration of tokens and not integrated directly into the web flow.

### Discrepancies (Implementation vs. README):
- The README mentions advanced web scraping using `Playwright` and `playwright-stealth` to extract job descriptions, but `scraper.py` currently only generates search URLs.
- The README references `main.py` as the orchestrator and entry point, but the actual entry point is `app.py`.
- Match scoring is advertised as a dynamic comparison but is currently hardcoded (e.g., returning 90 or 85) in `app.py`.

---

## 2. Future Implementations & Roadmap

Based on the analysis, the following technical implementations should be prioritized to fulfill the project's stated goals:

### Phase 1: Realize Web Scraping capabilities
- **Implement Playwright Scraper**: Overhaul `scraper.py` to utilize `playwright.sync_api` and `playwright-stealth` (as seen in `test_playwright.py`) to actually navigate to job boards, bypass bot protection, and scrape live job postings (Title, Company, Description, Apply Link).
- **Data Structuring**: Parse the scraped HTML using `BeautifulSoup4` (which is in `requirements.txt`) to clean the job descriptions for analysis.

### Phase 2: Advanced NLP & Dynamic Scoring
- **Dynamic Skill Extraction**: Replace the hardcoded `tech_stack` list in `analyzer.py` with an NLP-based approach (e.g., using SpaCy or a pre-trained HuggingFace model) to dynamically identify a vast array of skills and tools from both the resume and the scraped job descriptions.
- **Algorithmic Match Scoring**: Implement a matching engine that calculates the intersection of skills found in the resume against the skills required in the scraped job descriptions to generate a true, dynamic percentage match score.

### Phase 3: Data Persistence
- **Database Integration**: Integrate a database (e.g., SQLite for development, PostgreSQL for production) using an ORM like `SQLAlchemy`.
- **State Management**: Move away from relying solely on Flask `session` to store user profiles. Persist user data, uploaded resumes, scraped job history, and the "Apply Now" tracking (currently a mock endpoint in `app.py`) to the database.

### Phase 4: Automation & Alerts
- **Background Tasks**: Implement a background task queue (like Celery or APScheduler) to run scraping jobs periodically without blocking the Flask web server.
- **Telegram Integration**: Fully integrate `notifier.py` with the background tasks so users can receive daily/weekly automated alerts with their top job matches and the dynamically generated trend chart.

### Phase 5: Codebase Cleanup
- **Documentation**: Update `README.md` to accurately reflect the current usage (`python app.py` instead of `python main.py`).
- **Error Handling**: Improve error handling across the board, especially for the Playwright scraper, which is prone to timeouts and DOM changes.

---

## 3. Recent Improvements & Case Study (April 2026)

### Optimization for Technical Resumes
- **Dynamic Level Detection**: Refined `analyzer.py` to better distinguish between student-held "Senior" roles (e.g., Student Coordinator) and industry "Experienced" roles. Correctly identifies current B.Tech students as "Fresher" to ensure entry-level job matches.
- **Skill-Based Query Refinement**: Implemented automated skill cleaning and sorting (ascending length) to prioritize core technologies (Python, Django, AWS) over verbose descriptions, significantly improving scraper hit rates.
- **Multi-Source Dynamic Scraping**: Expanded `scraper.py` beyond Internshala to include dynamic scraping from **TimesJobs** and robust fallbacks for 10+ other major job boards.

### Case Study: Pranav Sahu Resume
- **Input**: Tech-heavy B.Tech resume with projects in Stable Diffusion, IoT, and Web Dev.
- **Issue**: Previously flagged as "Experienced" due to student lab roles, leading to irrelevant management job matches.
- **Resolution**: 
    - Correctly identified as **Fresher**.
    - Extracted core tech: **Linux, MySQL, Python, Flask, Django**.
    - Generated relevant results: **Linux Engineer, Backend Developer, and Software Internships**.
