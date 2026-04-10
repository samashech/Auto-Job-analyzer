from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=True)
    email = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    level = db.Column(db.String(50), nullable=True)
    skills = db.Column(db.Text, nullable=True) # Comma separated skills

class JobMatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(250), nullable=False)
    company = db.Column(db.String(250), nullable=True)
    url = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(100), nullable=True)
    job_type = db.Column(db.String(50), nullable=True) # Full-time, Internship, Freelance
