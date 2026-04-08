# RAIoT: Automated Job Market Intelligence & Matcher 🚀

**RAIoT** (Resume Analysis & Intelligent Opportunity Tracking) is a full-stack Python application that bridges the gap between a candidate's resume and the current job market.

---

## 🛠️ Tech Stack

* **Backend:** Python (Flask)
* **Data Science:** Pandas, Matplotlib, Seaborn
* **Automation:** Playwright, Playwright-Stealth
* **NLP:** PyPDF2, Regular Expressions

---

## 📂 Project Structure

```text
Project RAIoT/
├── app.py              # Flask Server
├── analyzer.py         # Resume Parsing
├── scraper.py          # Search URL Generator
├── visualizer.py       # Data Visualization
├── templates/          # HTML UI
├── static/             # Charts
└── uploads/            # Temp storage
🚀 Getting Started
1. Prerequisites
Make sure you have Python 3.10+ installed.

2. Installation
Run these commands in your terminal:

Bash
git clone [https://github.com/samashech/Auto-Job-analyzer.git](https://github.com/samashech/Auto-Job-analyzer.git)
cd RAIoT
python -m venv venv
source venv/bin/activate.fish
pip install -r requirements.txt
playwright install chromium
3. Running the App
Bash
python app.py
Visit http://127.0.0.1:5000 in your browser.

🛡️ Stealth & Anti-Bot Measures
This project implements playwright-stealth and randomized user-agents to mimic human behavior.

👨‍💻 Authors
Sameer, Pranav Sahu, and Saksham
Automating the path to the next big opportunity.
