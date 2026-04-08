# Project RAIoT: Automated Job Market Analyzer

Project RAIoT is a Python-based automation tool designed to help developers and AI engineers stay ahead of the job market. It scrapes real-time job listings from Indeed, extracts in-demand skills using natural language processing (NLP) techniques, calculates a personalized match score against your profile, and visualizes the results.

---

## 🚀 Features

- **Advanced Web Scraping**  
  Utilizes Playwright with stealth configurations to bypass anti-bot mechanisms and extract job descriptions from Indeed.

- **Skill Extraction**  
  Automatically identifies key technologies and skills (e.g., Python, SQL, Docker, Machine Learning) mentioned in job postings.

- **Match Scoring**  
  Compares your personal skill set against the top requirements of the current market to provide a percentage match score.

- **Data Visualization**  
  Generates clear, professional bar charts using Seaborn and Matplotlib to highlight trending technologies.

- **Telegram Notifications (Optional)**  
  Sends automated summaries and trend charts directly to your Telegram chat.

---

## 🛠 Tech Stack

- **Language**: Python 3.x  
- **Scraping**: Playwright, Playwright-Stealth  
- **Data Analysis**: Pandas, Regex (`re`)  
- **Visualization**: Matplotlib, Seaborn  
- **API Integration**: Telegram Bot API (via Requests)  

---

## 📋 Prerequisites

Before running the project, ensure you have:

- Python 3.8+
- Node.js (required for Playwright)

---

## ⚙️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/project-raiot.git
cd project-raiot
2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
3. Install dependencies
pip install -r requirements.txt
🚀 Usage
1. Configure your profile

Open main.py and update the MY_PROFILE_SKILLS list with your current skills.

2. Run the analyzer
python main.py
3. View results
Check the console for your Match Score
Open trend_chart.png to view the skill trends
🤖 Optional: Telegram Alerts

To enable Telegram notifications:

Create a bot via @BotFather and get your TELEGRAM_BOT_TOKEN
Get your TELEGRAM_CHAT_ID
Update credentials in notifier.py
Uncomment send_telegram_alert() in main.py
📂 Project Structure
project-raiot/
│
├── main.py          # Orchestrates full pipeline
├── scraper.py       # Handles job scraping
├── analyzer.py      # Skill extraction + scoring
├── visualizer.py    # Graph generation
├── notifier.py      # Telegram integration
├── requirements.txt # Dependencies
└── README.md
⚠️ Disclaimer

This tool is for educational purposes only. Always respect the robots.txt and Terms of Service of websites you scrape. Avoid excessive requests.
