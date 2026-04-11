import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from analyzer import analyze_resume
from scraper import get_dynamic_job_links
from visualizer import generate_chart
from models import db, User, JobMatch

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'

# Configure SQLite Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///raiot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Ensure required directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('static', exist_ok=True)

# Create tables inside the app context
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    """Serves the main dashboard HTML."""
    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serves uploaded resumes."""
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handles resume upload, analysis, and job matching."""
    if 'resume' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Save the resume to the uploads folder
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # 1. Run NLP Analysis to get dynamic skills and profile
    user_profile = analyze_resume(filepath)
    
    # Extract desired job type from request if user provided one (default: "Full-time")
    job_type = request.form.get('job_type', 'Full-time')
    
    # Phase 1: Save User to SQLite Database
    user = User(
        name=user_profile.get('name', 'Applicant'),
        email=user_profile.get('email', ''),
        phone=user_profile.get('phone', ''),
        level=user_profile['level'],
        skills=", ".join(user_profile['skills'])
    )
    db.session.add(user)
    db.session.commit()
    
    # 2. Build Search Links using the Scraper
    # Passing job_type so scraper knows what to search for (Full-time, Internship, Freelance)
    jobs = get_dynamic_job_links(user_profile['skills'], user_profile['level'], job_type)

    # Save Jobs to Database linked to the user
    for job in jobs:
        new_match = JobMatch(
            user_id=user.id,
            title=job.get('title', f"{user_profile['level']} Role"),
            company=job.get('company', 'Various Companies'),
            url=job.get('url', '#'),
            source=job.get('name', 'Web Scraper'),
            job_type=job_type,
            relevance_score=job.get('relevance_score', 0)
        )
        db.session.add(new_match)
    db.session.commit()

    # 3. Create Visualization
    chart_path = generate_chart(user_profile['skills'])

    return jsonify({
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "level": user.level,
        "skills": user_profile['skills'],
        "job_type": job_type,
        "jobs": jobs,
        "chart_url": "/static/trend_chart.png",
        "resume_url": f"/uploads/{file.filename}"
    })

@app.route('/fetch_jobs', methods=['POST'])
def fetch_jobs():
    """Handles fetching jobs based on manually entered skills."""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    skills_str = data.get('skills', '')
    level = data.get('level', 'Experienced')
    job_type = data.get('job_type', 'Full-time')

    # Parse skills
    skills = [s.strip() for s in skills_str.split(',')] if skills_str else []
    skills = [s for s in skills if s] # Remove empty strings

    # Build Search Links using the Scraper
    jobs = get_dynamic_job_links(skills, level, job_type)

    # Generate Visualization
    chart_path = generate_chart(skills) if skills else None

    return jsonify({
        "skills": skills,
        "jobs": jobs,
        "chart_url": "/static/trend_chart.png" if chart_path else None
    })

if __name__ == '__main__':
    app.run(debug=True)