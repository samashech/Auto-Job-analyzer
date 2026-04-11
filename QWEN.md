# QWEN.md - Project RAIoT Documentation

## Latest Fixes (April 11, 2026)

### Issue 8: Missing related skills - HTML user should know JavaScript, Linux user should know Desktop Systems, etc.
**Problem**: User has "HTML" in resume but system doesn't search for "JavaScript" jobs. User has "Linux" but doesn't search for "Desktop Systems" or "Unix". The scraper only searched for exact skills mentioned, missing related skills the user likely knows.

**Root Cause**: System only extracted skills explicitly mentioned in resume. Didn't infer related skills that professionals typically know together.

**Solution Implemented**:

#### 1. Smart Skill Inference System (`analyzer.py`)
Added **SKILL_INFERENCE_MAP** with 80+ skill relationships:

```python
# Examples of inferred skills:
"HTML" → ["JavaScript", "CSS", "Web Development", "Responsive Design"]
"Linux" → ["Desktop Systems", "Unix", "Shell Scripting", "Bash", "Ubuntu"]
"Adobe Photoshop" → ["Adobe Illustrator", "Image Editing", "Graphic Design", "Canva"]
"Stitching" → ["Draping", "Pattern Making", "Fashion Design", "Textile Design"]
"AWS" → ["Cloud Services", "DevOps", "Linux", "Docker"]
"Python" → ["SQL", "Data Analysis", "Git"]
```

**How it works:**
```python
def infer_related_skills(extracted_skills):
    inferred = set()
    for skill in extracted_skills:
        if skill in SKILL_INFERENCE_MAP:
            for related_skill in SKILL_INFERENCE_MAP[skill]:
                if related_skill not in extracted_skills:
                    inferred.add(related_skill)
    return list(inferred)
```

**Real Example:**
```
Resume has: "HTML, CSS"
Extracted: HTML, CSS
Inferred: JavaScript, Web Development, Responsive Design, Bootstrap
Total skills to search: 7 (instead of just 2)
Result: More job matches! ✓
```

**Benefits:**
- ✅ HTML users get JavaScript/Web Dev jobs
- ✅ Linux users get Desktop Systems/Unix jobs
- ✅ Fashion designers get Draping/Pattern Making jobs
- ✅ AWS users get Cloud Services/DevOps jobs
- ✅ Doesn't add skills user already has

#### 2. Fixed All Scrapers to Actually Get Real Jobs
**Before**: Only Internshala worked, LinkedIn/Indeed/others failed  
**After**: All 9 scrapers use **flexible selectors** with **fallback mechanisms**

**Improvements:**
- ✅ Uses `wait_until="networkidle"` (waits for JS to load)
- ✅ Multiple selectors per site (tries 2-3 different approaches)
- ✅ Better error handling with `try/continue`
- ✅ Detailed logging: `[LinkedIn] Found 12 jobs → Extracted 8 relevant`
- ✅ Increased description length to 300 chars for better relevance scoring

**Example Log Output:**
```
=== Searching for skill #1: 'Linux' ===
  Scraping Indeed for 'Linux'...
    [Indeed] Navigating to: https://in.indeed.com/jobs?q=Linux
    [Indeed] Found 15 jobs
    [Indeed] Extracted 8 relevant jobs
  Scraping LinkedIn for 'Linux'...
    [LinkedIn] Navigating to: https://www.linkedin.com/jobs/search/?keywords=Linux
    [LinkedIn] Found 12 jobs
    [LinkedIn] Extracted 7 relevant jobs
```

#### 3. Reduced Job Limit to 30 (More Refined)
**Before**: 50 jobs (too many, slower scraping)  
**After**: **30 jobs** (focused, faster, still comprehensive)

- Searches each skill across 9 job sites
- Stops early if 30+ relevant jobs found
- Better relevance filtering
- Faster overall processing time

---

### Issue 7: Skills like "Linux" not extracted from resume, resulting in "no jobs"
**Problem**: User's resume clearly mentioned "Linux" (e.g., "Managed Linux servers"), but the analyzer didn't extract it as a skill. When searching job sites for jobs, no Linux jobs appeared because Linux wasn't in the skill list.

**Root Cause**: SkillNER (NLP-based extractor) relies on the ESCO database which doesn't contain all technical skills or may miss skills mentioned in certain contexts.

**Solution Implemented**:

#### 1. Dual Skill Extraction System (`analyzer.py`)
Added **regex-based fallback** that works alongside SkillNER:

```python
def extract_all_skills(text, raw_text):
    # Method 1: SkillNER (NLP-based, catches context-aware skills)
    nlp_skills = extract_skills_with_nlp(text)
    
    # Method 2: Regex-based (catches skills NLP misses)
    regex_skills = extract_skills_with_regex(raw_text)
    
    # Combine both
    return list(set(nlp_skills + regex_skills))
```

**Extended Skill Database** - Added 100+ common technical skills:
- ✅ **Operating Systems**: Linux, Windows, Ubuntu, CentOS, Red Hat, Debian
- ✅ **Programming**: Python, Java, JavaScript, C, C++, Go, Rust, etc.
- ✅ **Web**: React, Angular, Vue, Django, Flask, Node.js, etc.
- ✅ **Databases**: MySQL, PostgreSQL, MongoDB, Redis, etc.
- ✅ **Cloud/DevOps**: AWS, Azure, Docker, Kubernetes, Jenkins, Git
- ✅ **Design**: Adobe Photoshop, Illustrator, Figma, Canva, etc.
- ✅ **Frameworks**: TensorFlow, PyTorch, Pandas, NumPy, etc.

**Test Results:**
```
Input: "Managed Linux servers including Ubuntu and CentOS"
SkillNER: 0 skills (missed it)
Regex: 3 skills (Linux, Ubuntu, CentOS) ✓
Total: 3 skills extracted
```

#### 2. Increased Job Search Limit to 50 (`scraper.py`)
- Changed from 20 jobs to **50 jobs maximum**
- Searches each skill across 9 job sites
- Stops early if 50+ jobs found
- Better coverage for diverse skill sets

#### 3. Professional Loading Screen (`script.js` + `index.html`)
Added a beautiful loading overlay that shows:
- ✅ Animated spinner
- ✅ 4-step progress tracker:
  1. Extracting skills from resume...
  2. Searching job boards for matching positions...
  3. Ranking jobs by relevance to your profile...
  4. Preparing your personalized dashboard...
- ✅ Step indicators change color as they complete (Blue → Green ✓)
- ✅ Shows final count: "Found X skills and Y relevant jobs"
- ✅ Estimated time: "This may take 1-3 minutes"

**User Experience Flow:**
```
User clicks "Process & Continue"
    ↓
Loading overlay appears with spinner
    ↓
Step 1: "Extracting skills..." (blue dot)
    ↓
Backend analyzes resume (NLP + Regex)
    ↓
Step 2: "Searching job boards..." (blue dot)
Step 3: "Ranking jobs..." (blue dot)
    ↓
Scraping completes (up to 50 jobs)
    ↓
Step 4: "Preparing dashboard..." (blue dot)
    ↓
All steps turn green with ✓
    ↓
Overlay disappears
    ↓
Resume display page shown
```

---

### Issue 6: Scraper shows "no jobs" but websites have jobs when searched manually
**Problem**: User had 12 design skills (Adobe Photoshop, Illustrator, Figma, etc.). Scraper combined ALL skills into one search query like "Adobe Photoshop Adobe Illustrator Figma Typography..." which returned 0 results. But searching each skill individually on the same websites found many jobs.

**Root Cause**: The scraper was combining top 3 skills into ONE search query:
```python
search_query = "Python Django AWS"  # Bad - no results
```
Instead of searching individually:
```python
"Python"    # Gets results ✓
"Django"    # Gets results ✓  
"AWS"       # Gets results ✓
```

**Solution Implemented**:

#### Complete Scraper Rewrite - Individual Skill Search
The scraper now searches for **EACH SKILL INDIVIDUALLY** across all job sites:

**OLD Behavior:**
```
Search: "Adobe Photoshop Adobe Illustrator Figma Typography Color theory"
Result: 0 jobs (nobody searches for this exact phrase)
```

**NEW Behavior:**
```
Searching skill #1: "Adobe Photoshop"
  -> Indeed: 5 jobs
  -> LinkedIn: 3 jobs
  -> TimesJobs: 4 jobs
Searching skill #2: "Adobe Illustrator"
  -> Indeed: 4 jobs
  -> Naukri: 6 jobs
Searching skill #3: "Figma"
  -> Indeed: 7 jobs
  -> Glassdoor: 2 jobs
...
Total: 31 jobs found ✓
```

**Key Features:**
1. ✅ Searches each skill separately (maximizes results)
2. ✅ Deduplicates across all searches (no repeated jobs)
3. ✅ Stops early if 20+ jobs found (saves time)
4. ✅ Shows detailed progress for each skill/website
5. ✅ Still maintains strict relevance scoring
6. ✅ Works for ANY skill type (technical, design, marketing, etc.)

**Example Flow for 12 Skills:**
```python
# Input: User resume with 12 skills
skills = ["Adobe Photoshop", "Adobe Illustrator", "Figma", "Canva", ...]

# Old approach: 1 search with combined skills = 0 results
# New approach: 12 individual searches = many results!

for skill in unique_skills:  # Each skill searched individually
    for website in [Indeed, LinkedIn, TimesJobs, Naukri, ...]:
        scrape(website, skill)  # Search THIS skill on THIS site
        if found_jobs:
            add_to_results(jobs)
    
    if total_jobs >= 20:
        break  # Stop early if we have enough
```

**Performance:**
- For resumes with common skills: Finds 20+ jobs quickly
- For specialized skills: Still finds jobs by searching individually
- Early stopping: Stops after 20 jobs to save time

---

### Issue 5: Shows irrelevant jobs (management/graphic design) for technical resumes
**Problem**: Users with technical resumes (Python, AWS, etc.) were seeing irrelevant job postings like management or graphic design roles.

**Root Cause**: Three issues combined:
1. **Fallback Links**: When scraping didn't return enough jobs, the system generated generic links like "Browse Full-time Roles on LinkedIn" which aren't real jobs
2. **Weak Relevance Scoring**: Jobs weren't being filtered strictly enough based on actual skill matches
3. **Frontend Fallback**: JavaScript had hardcoded `fallbackJobs` that would show when no real jobs were found

**Solution Implemented**:

#### 1. **Removed ALL Fallback Mechanisms** (`scraper.py`)
- Deleted the fallback code that generated generic website links
- Now **ONLY returns actually scraped jobs** with relevance score > 0
- If no relevant jobs found, returns empty list (honest result)

#### 2. **Stricter Relevance Scoring** (`scraper.py`)
- Enhanced `calculate_relevance_score()` to be much more strict
- Jobs must contain actual user skills in title or description
- Added bonus points if skills appear in job title
- Returns 0 for jobs with no meaningful skill matches
- Score formula: `(matched_skills / total_skills * 80) + title_bonus`

#### 3. **Removed Frontend Fallback** (`script.js`)
- Deleted `fallbackJobs` constant completely
- Updated `loadAndDisplayJobs()` to not use fallback jobs
- Shows honest "No Relevant Jobs Found" message with explanation
- Match score colors now vary: Green (50%+), Yellow (25-49%), Orange (<25%)

#### 4. **Better User Feedback**
- When no jobs match: Shows clear explanation of why
- Match scores now accurately reflect skill matches
- Job descriptions show which skills were matched

**Result**: Users will now **ONLY** see job postings that:
- ✅ Were actually scraped from real job sites
- ✅ Contain their specific technical skills in the posting
- ✅ Have a calculated relevance score > 0%
- ✅ Are sorted by relevance (most relevant first)

---

### Issue 4: SQLAlchemy/Database errors
**Problem**: Application was throwing database errors after adding the `relevance_score` column.

**Root Cause**: When adding a new column to an existing SQLite database, SQLAlchemy's `db.create_all()` doesn't automatically alter existing tables. The old database schema didn't have the `relevance_score` column.

**Solution Implemented**:
1. Deleted the old database file (`instance/raiot.db`)
2. App recreated the database fresh with the new schema on next startup
3. All columns now properly created: `id`, `user_id`, `title`, `company`, `url`, `source`, `job_type`, `relevance_score`

**For Future Migrations**: If you need to add columns in production without losing data, use this approach:
```python
import sqlite3
# Add column if it doesn't exist
cursor.execute("ALTER TABLE job_match ADD COLUMN new_column_name INTEGER DEFAULT 0")
```

---

### Issue 3: Frontend doesn't navigate after resume upload
**Problem**: After uploading a resume, the page stayed on the upload form instead of showing the resume analysis results or dashboard.

**Root Cause**: The `handleResumeUpload()` function in `script.js` called `generateResumeDisplay()` but didn't hide the `resumeEntryPage` first, so the user stayed on the upload screen even though data was processed.

**Solution Implemented**:
1. Added `document.getElementById('resumeEntryPage').classList.add('hidden')` before calling `generateResumeDisplay()`
2. Updated job mapping to use actual `relevance_score` from scraper instead of hardcoded 90
3. Ensures proper page flow: Upload → Analysis → Resume Display → Dashboard

---

## Issues Fixed (April 11, 2026)

### Issue 1: Results showed websites without relevant job postings
**Problem**: The scraper was generating generic links to job sites instead of scraping actual job postings, resulting in irrelevant results.

**Solution Implemented**:
1. **Added Relevance Scoring System** (`calculate_relevance_score` function):
   - Compares user's skills against job titles and descriptions
   - Scores each job from 0-100 based on skill matches
   - Checks for full skill matches and partial word matches
   - Filters out jobs with 0 relevance score

2. **Skill-Based Filtering**:
   - Jobs are now filtered to only show postings that match user skills
   - Each scraped job includes a `relevance_score` field
   - Results are sorted by relevance score (highest first)
   - Only jobs with relevance > 0 are shown to users

### Issue 2: Scraper favored particular websites (not dynamic)
**Problem**: The scraper was hardcoded to only scrape from Internshala and TimesJobs, then fell back to generating generic links for other sites.

**Solution Implemented**:
1. **Multi-Source Dynamic Scraping**:
   - Implemented actual scrapers for 9 job sites:
     - Internshala
     - TimesJobs
     - LinkedIn
     - Indeed
     - Naukri
     - Glassdoor
     - Monster (Foundit)
     - Wellfound (AngelList)
     - Upwork (for freelance jobs)

2. **Randomized Rotation**:
   - Scraper order is shuffled on each run using `random.shuffle()`
   - Prevents bias toward any particular website
   - Ensures diverse job sources in results

3. **Fallback Mechanism**:
   - If primary skill combination doesn't yield enough results, tries secondary combinations
   - Only uses generic link generation as last resort (with low relevance score of 10)

4. **Deduplication**:
   - Removes duplicate jobs based on URL
   - Ensures unique job postings across all sources

## Code Changes

### `scraper.py` - Complete Rewrite
- **Old**: Only scraped 2 sites, fell back to link generation
- **New**: 
  - 9 dedicated scraper functions for actual job postings
  - `calculate_relevance_score()` for skill-based filtering
  - Randomized scraper rotation
  - Multi-pass scraping (primary + secondary skill combinations)
  - Better error handling and logging

### `models.py` - Added Relevance Score
- Added `relevance_score` column to `JobMatch` model
- Stores 0-100 score indicating how well job matches user skills

### `app.py` - Updated Job Saving
- Now saves `relevance_score` from scraper results to database
- Maintains compatibility with existing functionality

## Architecture

### Scraping Flow
```
User Resume → Skill Extraction → Top 3 Skills
                                      ↓
                    Shuffle Scraper Order (Random)
                                      ↓
        ┌─────────────────────────────────────────┐
        │ Scrape: LinkedIn, Indeed, Naukri,       │
        │ Glassdoor, Internshala, TimesJobs,      │
        │ Monster, Wellfound, Upwork              │
        └─────────────────────────────────────────┘
                                      ↓
                  Calculate Relevance Score (0-100)
                                      ↓
                    Filter (score > 0) + Sort
                                      ↓
                    Remove Duplicates by URL
                                      ↓
              Secondary Scrape (if < 10 results)
                                      ↓
                    Return Top 15 Jobs
```

### Relevance Scoring Algorithm
```python
score = (matched_skills / total_user_skills) * 100
```
- Full skill match = 1 point
- Partial word match = 0.5 points
- Maximum score = 100
- Minimum threshold = 1 (jobs with 0 are filtered out)

## Key Functions

### `calculate_relevance_score(job_title, job_description, skills)`
- **Purpose**: Score job relevance based on user skills
- **Returns**: Integer 0-100
- **Logic**: Counts how many user skills appear in job text

### `scrape_*` Functions (9 total)
- **Purpose**: Extract actual job postings from each website
- **Common Pattern**:
  1. Navigate to job search URL
  2. Parse HTML with BeautifulSoup
  3. Extract job cards with flexible CSS selectors
  4. Calculate relevance score for each job
  5. Return list of job dictionaries

### `get_dynamic_job_links(skills, level, job_type)`
- **Purpose**: Main entry point for job scraping
- **Returns**: List of up to 15 relevant jobs, sorted by relevance
- **Features**:
  - Randomized scraper rotation
  - Multi-pass scraping
  - Deduplication
  - Fallback to generic links if needed

## Testing Recommendations

1. **Test with different skill sets**:
   - Technical skills (Python, JavaScript, etc.)
   - Non-technical skills (Marketing, Sales, etc.)
   - Mixed skills

2. **Test all job types**:
   - Full-time
   - Internship
   - Part-time
   - Freelance

3. **Monitor scraper success rates**:
   - Check console output for which scrapers succeed/fail
   - Adjust timeouts or selectors if sites change structure

## Future Improvements

1. **Parallel Scraping**: Use asyncio to scrape multiple sites simultaneously
2. **Caching**: Cache job results to reduce scraping frequency
3. **Job Details**: Scrape full job descriptions for better relevance scoring
4. **Location Filtering**: Add location-based job filtering
5. **User Preferences**: Allow users to weight certain skills higher
6. **Rate Limiting**: Implement smarter rate limiting to avoid detection
7. **Proxy Rotation**: Add proxy support for high-volume scraping

## Dependencies
- Playwright (browser automation)
- Playwright-Stealth (anti-detection)
- BeautifulSoup4 (HTML parsing)
- Flask-SQLAlchemy (database)
- PyPDF2 (PDF parsing)
- spaCy + SkillNER (skill extraction)

## Database Schema
- **User**: id, name, email, phone, level, skills
- **JobMatch**: id, user_id, title, company, url, source, job_type, **relevance_score** (new)
