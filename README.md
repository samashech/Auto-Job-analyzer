1 - # Auto-Job-analyzer                                                             │
│  1 + # Project RAIoT: Automated Job Market Analyzer                                  │
│  2 +                                                                                 │
│  3 + Project RAIoT is a Python-based automation tool designed to help developers and │
│    AI engineers stay ahead of the job market. It scrapes real-time job listings from │
│    Indeed, extracts in-demand skills using natural language processing (NLP)         │
│    techniques, calculates a personalized match score against your profile, and       │
│    visualizes the results.                                                           │
│  4 +                                                                                 │
│  5 + ## 🚀 Features                                                                  │
│  6 +                                                                                 │
│  7 + - **Advanced Web Scraping**: Utilizes `Playwright` with stealth configurations  │
│    to bypass anti-bot mechanisms and extract job descriptions from Indeed.           │
│  8 + - **Skill Extraction**: Automatically identifies key technologies and skills    │
│    (e.g., Python, SQL, Docker, Machine Learning) mentioned in job postings.          │
│  9 + - **Match Scoring**: Compares your personal skill set against the top           │
│    requirements of the current market to provide a percentage match score.           │
│ 10 + - **Data Visualization**: Generates clear, professional bar charts using        │
│    `Seaborn` and `Matplotlib` to highlight trending technologies.                    │
│ 11 + - **Telegram Notifications**: (Optional) Sends automated summaries and trend    │
│    charts directly to your Telegram chat.                                            │
│ 12 +                                                                                 │
│ 13 + ## 🛠 Tech Stack                                                                │
│ 14 +                                                                                 │
│ 15 + - **Language**: Python 3.x                                                      │
│ 16 + - **Scraping**: Playwright, Playwright-Stealth                                  │
│ 17 + - **Data Analysis**: Pandas, Re (Regex)                                         │
│ 18 + - **Visualization**: Matplotlib, Seaborn                                        │
│ 19 + - **API Integration**: Telegram Bot API (via Requests)                          │
│ 20 +                                                                                 │
│ 21 + ## 📋 Prerequisites                                                             │
│ 22 +                                                                                 │
│ 23 + Before running the project, ensure you have the following installed:            │
│ 24 + - Python 3.8+                                                                   │
│ 25 + - Node.js (required for Playwright)                                             │
│ 26 +                                                                                 │
│ 27 + ## ⚙ Installation                                                              │
│ 28 +                                                                                 │
│ 29 + 1. **Clone the repository**:                                                    │
│ 30 +    ```bash                                                                      │
│ 31 +    git clone https://github.com/your-username/project-raiot.git                 │
│ 32 +    cd project-raiot                                                             │
│ 33 +    ```                                                                          │
│ 34 +                                                                                 │
│ 35 + 2. **Create and activate a virtual environment**:                               │
│ 36 +    ```bash                                                                      │
│ 37 +    python -m venv venv                                                          │
│ 38 +    source venv/bin/activate  # On Windows: venv\Scripts\activate                │
│ 39 +    ```                                                                          │
│ 40 +                                                                                 │
│ 41 + 3. **Install dependencies**:                                                    │
│ 42 +    ```bash                                                                      │
│ 43 +    pip install -r requirements.txt                                              │
│ 44 +    ```                                                                          │
│ 45 +                                                                                 │
│ 46 + 4. **Install Playwright browsers**:                                             │
│ 47 +    ```bash                                                                      │
│ 48 +    playwright install chromium                                                  │
│ 49 +    ```                                                                          │
│ 50 +                                                                                 │
│ 51 + ## 🚀 Usage                                                                     │
│ 52 +                                                                                 │
│ 53 + 1. **Configure your profile**: Open `main.py` and update the                    │
│    `MY_PROFILE_SKILLS` list with your current skills.                                │
│ 54 + 2. **Run the analyzer**:                                                        │
│ 55 +    ```bash                                                                      │
│ 56 +    python main.py                                                               │
│ 57 +    ```                                                                          │
│ 58 + 3. **View Results**:                                                            │
│ 59 +    - Check the console for your **Match Score**.                                │
│ 60 +    - Open `trend_chart.png` in the project directory to see the skill           │
│    visualization.                                                                    │
│ 61 +                                                                                 │
│ 62 + ## 🤖 Optional: Telegram Alerts                                                 │
│ 63 +                                                                                 │
│ 64 + To enable Telegram notifications:                                               │
│ 65 + 1. Create a bot via [@BotFather](https://t.me/botfather) and get your           │
│    `TELEGRAM_BOT_TOKEN`.                                                             │
│ 66 + 2. Get your `TELEGRAM_CHAT_ID`.                                                 │
│ 67 + 3. Update the credentials in `notifier.py`.                                     │
│ 68 + 4. Uncomment the `send_telegram_alert` call in `main.py`.                       │
│ 69 +                                                                                 │
│ 70 + ## 📂 Project Structure                                                         │
│ 71 +                                                                                 │
│ 72 + - `main.py`: The central orchestrator for the scraping, analysis, and           │
│    notification pipeline.                                                            │
│ 73 + - `scraper.py`: Handles stealth browsing and job data extraction.               │
│ 74 + - `analyzer.py`: Contains logic for skill extraction and match score            │
│    calculation.                                                                      │
│ 75 + - `visualizer.py`: Generates the trend charts.                                  │
│ 76 + - `notifier.py`: Manages Telegram API communications.                           │
│ 77 + - `requirements.txt`: Lists all Python dependencies.                            │
│ 78 +                               
