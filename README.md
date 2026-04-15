# RAIoT: Resume Analysis & Intelligent Opportunity Tracking 🚀

**RAIoT** is a full-stack web application designed to bridge the gap between a candidate's resume and the current job market. It analyzes your resume, extracts your skills, scrapes live job postings, and intelligently matches you with the best opportunities.

---

## 🚀 Features

- **Automated Resume Parsing**: Upload your PDF resume, and RAIoT will extract your core skills and determine your experience level using Natural Language Processing (spaCy).
- **Live Job Market Scraping**: Utilizes `Playwright` with stealth configurations to bypass anti-bot mechanisms and scrape real-time job postings from various platforms.
- **Intelligent Match Scoring**: Dynamically compares your extracted skills against job requirements to calculate a personalized percentage match score.
- **Data Visualization**: Generates professional trend charts using `Matplotlib` and `Seaborn` to show you which of your skills are most in demand.
- **Modern Interactive Dashboard**: A sleek, responsive frontend built with Next.js, Tailwind CSS, and Framer Motion for a seamless user experience.
- **Telegram Notifications**: (Optional) Get automated alerts, summaries, and trend charts sent directly to your Telegram.

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js (React 19)
- **Styling**: Tailwind CSS v4
- **Language**: TypeScript
- **Animations & Icons**: Framer Motion, Lucide React

### Backend & Data Science
- **Server**: Python 3.10+ with Flask
- **Database**: SQLite with SQLAlchemy (via Flask-SQLAlchemy)
- **Scraping**: Playwright, Playwright-Stealth, BeautifulSoup4
- **NLP & Parsing**: spaCy, PyPDF2
- **Visualization**: Matplotlib, Seaborn, Pandas
- **API Integration**: Telegram Bot API (via Requests)

---

## 📂 Project Structure

```
Project RAIoT/
├── frontend/               # Next.js frontend application
│   ├── src/app/            # Next.js App Router pages and layouts
│   └── src/components/     # Reusable React components
├── app.py                  # Main Flask application entry point
├── analyzer.py             # Resume parsing and NLP skill extraction logic
├── scraper.py              # Stealth web scraping for job postings
├── visualizer.py           # Generation of skill demand trend charts
├── models.py               # SQLAlchemy database models
├── notifier.py             # Telegram notification integration
├── run.sh                  # Shell script to run both frontend and backend
└── requirements.txt        # Python backend dependencies
```

---

## ⚙️ Installation & Setup

### 1. Prerequisites
- Python 3.10 or higher
- Node.js (v18+) and npm

### 2. Clone the repository
```bash
git clone https://github.com/your-username/project-raiot.git
cd "project-raiot"
```

### 3. Backend Setup (Python)
Create and activate a virtual environment, then install dependencies:
```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate
# Activate (Windows)
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (Required for scraping)
playwright install chromium
```

### 4. Frontend Setup (Node.js)
Install the Next.js dependencies:
```bash
cd frontend
npm install
cd ..
```

---

## 🚀 Usage

You can run both the Next.js frontend and the Flask backend simultaneously using the provided startup script:

```bash
chmod +x run.sh
./run.sh
```

**What this script does:**
- Starts the **Next.js frontend** in the background on `http://localhost:3000`.
- Starts the **Flask backend** in the foreground on `http://localhost:5000` so you can view live scraping logs and API activity.
- Gracefully shuts down both servers when you press `Ctrl+C`.

**Accessing the Application:**
- **Dashboard**: Open your browser and navigate to `http://localhost:3000`
- **Backend API**: `http://localhost:5000`

---

## 🤖 Optional: Telegram Alerts

To enable Telegram notifications for automated job matches:
1. Create a bot via [@BotFather](https://t.me/botfather) and get your `TELEGRAM_BOT_TOKEN`.
2. Get your `TELEGRAM_CHAT_ID`.
3. Update the credentials in `notifier.py`.

---

## ⚠️ Disclaimer

This tool is for educational purposes only. Always respect the `robots.txt` and Terms of Service of any website you scrape. Use responsibly and avoid excessive requests. The scraping implementation uses stealth techniques, but it is your responsibility to use them ethically.

---

## 👨‍💻 Authors

**Sameer, Pranav Sahu, and Saksham**  
*Automating the path to the next big opportunity.*  
Built with ❤️ for AI Engineers and Developers.