from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(50), nullable=True)
    level = db.Column(db.String(50), nullable=True)
    skills = db.Column(db.Text, nullable=True) # Comma separated skills
    location = db.Column(db.String(100), nullable=True)
    job_type = db.Column(db.String(50), nullable=True)
    job_role = db.Column(db.String(100), nullable=True)
    resume_url = db.Column(db.String(256), nullable=True)
    
    # Extended Profile Fields (Frontend Support)
    about = db.Column(db.Text, nullable=True)
    projects = db.Column(db.Text, nullable=True) # Comma separated
    achievements = db.Column(db.Text, nullable=True) # Comma separated
    education = db.Column(db.Text, nullable=True) # Comma separated
    certificates = db.Column(db.Text, nullable=True) # Comma separated
    positions_of_responsibility = db.Column(db.Text, nullable=True) # Comma separated
    social_github = db.Column(db.String(256), nullable=True)
    social_linkedin = db.Column(db.String(256), nullable=True)
    social_portfolio = db.Column(db.String(256), nullable=True)
    photo_data_url = db.Column(db.Text, nullable=True)

    # Relationship
    applications = db.relationship('Application', backref='user', lazy=True)

class JobMatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(250), nullable=False)
    company = db.Column(db.String(250), nullable=True)
    url = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(100), nullable=True)
    job_type = db.Column(db.String(50), nullable=True) # Full-time, Internship, Freelance
    relevance_score = db.Column(db.Integer, default=0) # 0-100 score based on skill match
    saved = db.Column(db.Boolean, default=False) # User bookmarked this job
    
    # Extended Job Fields (Frontend Support)
    description = db.Column(db.Text, nullable=True)
    salary = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(250), nullable=True)
    skills_required = db.Column(db.Text, nullable=True) # Comma separated
    region = db.Column(db.String(50), nullable=True) # India / International
    state_or_continent = db.Column(db.String(100), nullable=True)

    # Relationship
    applications = db.relationship('Application', backref='job', lazy=True)

class Application(db.Model):
    """Tracks jobs the user has applied to and their status."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job_match.id'), nullable=False)
    status = db.Column(db.String(50), default='Applied')  # Applied, Interview, Rejected, Selected
    applied_date = db.Column(db.DateTime, default=datetime.utcnow)
