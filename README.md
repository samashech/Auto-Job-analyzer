# Align 🚀

**Align** (formerly RAIoT) is an intelligent, full-stack platform designed to bridge the gap between a candidate's resume and the current job market. It analyzes your resume, extracts your core skills using NLP, orchestrates AI-driven job scraping, and matches you with your best opportunities in real-time.

---

## 🚀 Features

- **Automated Resume Parsing**: Upload your PDF/DOCX resume, and Align will extract your core skills and determine your experience level using Natural Language Processing (spaCy).
- **AI-Powered Job Automation**: Integrates with **n8n** and **Ollama (LLM)** to intelligently scrape, clean, and structure messy job board data into usable JSON formats.
- **Rich Job Market Intelligence**: Scrapes real-time postings including comprehensive job descriptions, direct application URLs, salaries, and employment types using Apify.
- **Intelligent Match Scoring**: Dynamically compares your extracted skills against job requirements to calculate a personalized percentage match score.
- **Data Visualization**: Generates professional trend charts using `Matplotlib` and `Seaborn` to show you which of your skills are most in demand.
- **Modern Interactive Dashboard**: A sleek, responsive frontend built with Next.js, Tailwind CSS, and Framer Motion featuring expandable job details and real-time data streaming.
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
- **Automation & Orchestration**: n8n (Node-Based Workflow Automation)
- **AI & LLMs**: Ollama (Local AI execution)
- **Scraping**: Apify, Playwright, BeautifulSoup4
- **NLP & Parsing**: spaCy, PyPDF2
- **Visualization**: Matplotlib, Seaborn, Pandas

---

## 📂 Project Structure

```
Align/
├── frontend/               # Next.js frontend application
│   ├── src/app/            # App Router pages (Dashboard, Auth, etc.)
│   ├── src/components/     # Reusable UI and layout components
│   └── src/lib/            # Types, utilities, and application state
├── app.py                  # Main Flask application entry point
├── analyzer.py             # Resume parsing and NLP skill extraction logic
├── models.py               # SQLAlchemy database models
├── visualizer.py           # Generation of skill demand trend charts
├── scraper.py              # Legacy/Fallback scraping implementations
├── instance/               # Contains the SQLite database (raiot.db)
├── uploads/                # Local storage for uploaded resumes
├── requirements.txt        # Python backend dependencies
└── run.sh                  # Shell script to orchestrate frontend & backend startup
```

---

## ⚙️ Installation & Setup

### 1. Prerequisites
Ensure you have the following installed on your system:
- **Python 3.10** or higher
- **Node.js (v18+)** and npm
- **n8n**: For workflow automation ([Installation Guide](https://docs.n8n.io/hosting/))
- **Ollama**: For local AI parsing ([Download Ollama](https://ollama.com/))
- **Apify Account**: For running the LinkedIn/job board scrapers.

### 2. Clone the Repository
```bash
git clone https://github.com/samashech/Align.git
cd Align
```

### 3. Backend Setup (Flask/Python)
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

# Install Playwright browsers (Required for fallback scraping)
playwright install chromium
```

### 4. Frontend Setup (Next.js)
Install the frontend dependencies:
```bash
cd frontend
npm install
cd ..
```

### 5. AI & Automation Setup (Ollama & n8n)
To power the intelligent data extraction, you need to configure the AI pipeline:

1. **Start Ollama & Pull the Model**:
   Open a terminal and ensure your local Ollama instance has the required model:
   ```bash
   ollama pull llama3.1:8b
   ```
2. **Configure n8n**:
   - Start your n8n instance.
   - Import your workflow into n8n.
   - Ensure the **Apify node** is configured with your API key.
   - Ensure the **Ollama node** points to your local instance (usually `http://localhost:11434`) and is set to use the `llama3.1:8b` model.
   - Ensure the **HTTP Request node** is configured to POST data back to `http://localhost:5000/api/receive-n8n-jobs`.

---

## 🚀 Usage

You can run both the Next.js frontend and the Flask backend simultaneously using the provided startup script from the root directory:

```bash
chmod +x run.sh
./run.sh
```

**What this script does:**
- Starts the **Next.js frontend** in the background on `http://localhost:3000`.
- Starts the **Flask backend** in the foreground on `http://localhost:5000` so you can view live scraping logs and API activity.
- Gracefully shuts down both servers when you press `Ctrl+C`.

**Accessing the Application:**
- **Web Dashboard**: Navigate to `http://localhost:3000`
- **Backend API**: `http://localhost:5000`

---

## 👨‍💻 Authors

**Sameer, Pranav Sahu, and Saksham**  
*Automating the path to the next big opportunity.*  
Built with ❤️ for AI Engineers and Developers.