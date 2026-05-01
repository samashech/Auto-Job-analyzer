import os
import json
import time
import threading
import hashlib
import secrets
from queue import Queue, Empty
from flask import Flask, render_template, request, jsonify, send_from_directory, Response, session
from flask_cors import CORS
from analyzer import analyze_resume
from scraper import get_dynamic_job_links
from visualizer import generate_chart
from models import db, User, JobMatch, Application

app = Flask(__name__)
CORS(app, supports_credentials=True)
UPLOAD_FOLDER = 'uploads'

# Configure SQLite Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///raiot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'raiot-secret-key-2026'
db.init_app(app)

# Global stores for real-time job streaming
# Key: user_id, Value: {'jobs': [], 'scraping': bool, 'queue': Queue, 'finished': bool}
scraping_state = {}

def stop_scraping_for_user(user_id):
    """Stop any active scraping thread for a user by marking state as finished."""
    state = scraping_state.get(user_id)
    if state and state.get('scraping'):
        print(f"🛑 Stopping active scraping for user {user_id}")
        state['scraping'] = False
        state['finished'] = True
        # Send completion signal to any waiting SSE clients
        state['queue'].put({
            'type': 'complete',
            'data': {'total_jobs': len(state.get('jobs', [])), 'stopped': True}
        })

# Ensure required directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('static', exist_ok=True)

# Create tables inside the app context
with app.app_context():
    db.create_all()
    # Migration: Add new columns to existing tables if they don't exist
    import sqlite3
    db_path = os.path.join(app.instance_path, 'raiot.db')
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("ALTER TABLE job_match ADD COLUMN saved INTEGER DEFAULT 0")
            print("✅ Added 'saved' column to job_match table")
        except sqlite3.OperationalError as e:
            if "duplicate column" not in str(e).lower():
                pass  # Column already exists
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS application (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    job_id INTEGER NOT NULL,
                    status VARCHAR(50) DEFAULT 'Applied',
                    applied_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user(id),
                    FOREIGN KEY (job_id) REFERENCES job_match(id)
                )
            """)
            print("✅ Created 'application' table")
        except sqlite3.OperationalError as e:
            pass  # Table already exists
        
        try:
            cursor.execute("ALTER TABLE user ADD COLUMN about TEXT")
            cursor.execute("ALTER TABLE user ADD COLUMN projects TEXT")
            cursor.execute("ALTER TABLE user ADD COLUMN achievements TEXT")
            cursor.execute("ALTER TABLE user ADD COLUMN education TEXT")
            cursor.execute("ALTER TABLE user ADD COLUMN certificates TEXT")
            cursor.execute("ALTER TABLE user ADD COLUMN positions_of_responsibility TEXT")
            cursor.execute("ALTER TABLE user ADD COLUMN social_github VARCHAR(256)")
            cursor.execute("ALTER TABLE user ADD COLUMN social_linkedin VARCHAR(256)")
            cursor.execute("ALTER TABLE user ADD COLUMN social_portfolio VARCHAR(256)")
            cursor.execute("ALTER TABLE user ADD COLUMN photo_data_url TEXT")
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute("ALTER TABLE job_match ADD COLUMN description TEXT")
        except sqlite3.OperationalError:
            pass
            
        try:
            cursor.execute("ALTER TABLE job_match ADD COLUMN job_function VARCHAR(150)")
        except sqlite3.OperationalError:
            pass
            
        try:
            cursor.execute("ALTER TABLE job_match ADD COLUMN expiry_date VARCHAR(50)")
        except sqlite3.OperationalError:
            pass

        try:
            cursor.execute("ALTER TABLE job_match ADD COLUMN salary VARCHAR(100)")
            cursor.execute("ALTER TABLE job_match ADD COLUMN location VARCHAR(250)")
            cursor.execute("ALTER TABLE job_match ADD COLUMN skills_required TEXT")
            cursor.execute("ALTER TABLE job_match ADD COLUMN region VARCHAR(50)")
            cursor.execute("ALTER TABLE job_match ADD COLUMN state_or_continent VARCHAR(100)")
        except sqlite3.OperationalError:
            pass

        conn.commit()
        conn.close()

# ============ PASSWORD HASHING HELPERS ============
def hash_password(password):
    """Hash password with salt using SHA-256."""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${password_hash}"

def verify_password(password, stored_hash):
    """Verify password against stored hash."""
    try:
        salt, hash_value = stored_hash.split('$')
        return hashlib.sha256((password + salt).encode()).hexdigest() == hash_value
    except:
        return False

# ============ OTP STORAGE (In-memory for simplicity) ============
otp_store = {}  # {email: {'otp': '123456', 'expires': timestamp}}

def background_scrape_job(user_id, skills, level, job_type, experience_level, location, job_role=""):
    """Background thread to send scraping request to n8n webhook."""
    with app.app_context():
        state = scraping_state.get(user_id)
        if not state:
            print(f"⚠️ No scraping state for user {user_id}")
            return
        
        print(f"🚀 Sending background scrape request to n8n for user {user_id}")
        print(f"   Role: {job_role}, Skills: {len(skills)}, Level: {level}, Type: {job_type}")
        
        state['scraping'] = True
        state['total_skills'] = len(skills)
        state['processed_skills'] = 0
        
        payload = {
            "user_id": user_id,
            "skills": skills,
            "level": level,
            "job_type": job_type,
            "experience_level": experience_level,
            "location": location,
            "job_role": job_role
        }
        
        n8n_webhook_url = "http://localhost:5678/webhook-test/853c96d1-4517-402d-a08d-284c62166d58"
        
        try:
            import requests
            response = requests.post(n8n_webhook_url, json=payload, timeout=5)
            print(f"✅ Sent to n8n! Status: {response.status_code}")
            
            # Since n8n handles the scraping, we'll mark as complete for the local synchronous queue 
            # Or we let it remain true and `/api/receive-n8n-jobs` will handle completion when n8n is done.
            # But the frontend might expect some immediate feedback. We will leave it running, 
            # and when n8n finishes, it can signal complete. Since n8n is asynchronous, we just return.
            # We won't set state['scraping'] = False here, we wait for a completion webhook from n8n ideally.
            # But for now, we leave it open so frontend keeps waiting for jobs.
            
        except Exception as e:
            print(f"❌ Failed to reach n8n: {e}")
            state['scraping'] = False
            state['queue'].put({
                'type': 'error',
                'data': {'message': f'Failed to reach n8n scraper: {e}'}
            })
            state['finished'] = True

# ============ AUTHENTICATION ROUTES ============

@app.route('/auth/signup', methods=['POST'])
def signup():
    """Create a new user account."""
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    name = data.get('name', '').strip()

    # Validation
    if not email or not password or not name:
        return jsonify({'error': 'Email, password, and name are required'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    # Check if email already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'Email already registered. Please login instead.'}), 409

    # Create new user with hashed password
    try:
        new_user = User(
            name=name,
            email=email,
            password_hash=hash_password(password)
        )
        db.session.add(new_user)
        db.session.commit()

        # Store user info in session
        session['user_id'] = new_user.id
        session['user_email'] = new_user.email
        session['user_name'] = new_user.name

        return jsonify({
            'success': True,
            'message': 'Account created successfully!',
            'user': {
                'id': new_user.id,
                'name': new_user.name,
                'email': new_user.email
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"❌ Signup error: {e}")
        return jsonify({'error': 'Failed to create account'}), 500


@app.route('/auth/login', methods=['POST'])
def login():
    """Login user with email and password."""
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    # Validation
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    # Find user by email
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Email not found. Please create an account first.'}), 404

    # Verify password
    if not verify_password(password, user.password_hash):
        return jsonify({'error': 'Incorrect password. Please try again.'}), 401

    # Stop any active scraping for this user (from previous session)
    stop_scraping_for_user(user.id)

    # Store user info in session
    session['user_id'] = user.id
    session['user_email'] = user.email
    session['user_name'] = user.name

    # Check if user already has resume data (skills populated)
    has_resume_data = bool(user.skills and user.level)

    # Check if profile is COMPLETE (all fields filled)
    profile_complete = all([user.skills, user.level, user.location, user.job_type, user.job_role])

    # If user has existing jobs in database, note that too
    existing_jobs_count = JobMatch.query.filter_by(user_id=user.id).count()

    return jsonify({
        'success': True,
        'message': 'Login successful!',
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'skills': user.skills,
            'level': user.level,
            'location': user.location,
            'job_type': user.job_type,
            'job_role': user.job_role,
            'resume_url': user.resume_url,
            'about': user.about,
            'projects': user.projects,
            'achievements': user.achievements,
            'education': user.education,
            'certificates': user.certificates,
            'positions_of_responsibility': user.positions_of_responsibility,
            'social_github': user.social_github,
            'social_linkedin': user.social_linkedin,
            'social_portfolio': user.social_portfolio,
            'photo_data_url': user.photo_data_url,
            'has_resume_data': has_resume_data,
            'profile_complete': profile_complete,
            'existing_jobs_count': existing_jobs_count
        }
    }), 200


@app.route('/auth/logout', methods=['POST'])
def logout():
    """Logout user, stop any active scraping, and clear session."""
    user_id = session.get('user_id')

    # Stop any active scraping for this user
    if user_id:
        print(f"🚪 User {user_id} logging out - stopping scraping")
        stop_scraping_for_user(user_id)

    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200


@app.route('/auth/check-session', methods=['GET'])
def check_session():
    """Check if user is logged in."""
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            profile_complete = all([user.skills, user.level, user.location, user.job_type, user.job_role])
            return jsonify({
                'logged_in': True,
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'skills': user.skills,
                    'level': user.level,
                    'location': user.location,
                    'job_type': user.job_type,
                    'job_role': user.job_role,
                    'resume_url': user.resume_url,
                    'about': user.about,
                    'projects': user.projects,
                    'achievements': user.achievements,
                    'education': user.education,
                    'certificates': user.certificates,
                    'positions_of_responsibility': user.positions_of_responsibility,
                    'social_github': user.social_github,
                    'social_linkedin': user.social_linkedin,
                    'social_portfolio': user.social_portfolio,
                    'photo_data_url': user.photo_data_url,
                    'has_resume_data': bool(user.skills and user.level),
                    'profile_complete': profile_complete
                }
            }), 200

    return jsonify({'logged_in': False}), 200


@app.route('/auth/forgot-password', methods=['POST'])
def forgot_password():
    """Send OTP to user's email (simulated)."""
    data = request.get_json()
    email = data.get('email', '').strip().lower()

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    # Check if email exists
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Email not found. Please create an account first.'}), 404

    # Generate OTP (6 digits)
    import random
    otp = str(random.randint(100000, 999999))

    # Store OTP with expiration (5 minutes)
    otp_store[email] = {
        'otp': otp,
        'expires': time.time() + 300  # 5 minutes
    }

    # In production, send email here
    print(f"🔐 OTP for {email}: {otp}")

    return jsonify({
        'success': True,
        'message': 'OTP sent to your email. Check console for demo.',
        'demo_otp': otp  # Remove in production
    }), 200


@app.route('/auth/reset-password', methods=['POST'])
def reset_password():
    """Reset password using OTP."""
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    otp = data.get('otp', '')
    new_password = data.get('new_password', '')

    # Validation
    if not email or not otp or not new_password:
        return jsonify({'error': 'All fields are required'}), 400

    if len(new_password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    # Verify OTP
    if email not in otp_store:
        return jsonify({'error': 'OTP not found. Please request a new one.'}), 400

    otp_data = otp_store[email]

    # Check if OTP expired
    if time.time() > otp_data['expires']:
        del otp_store[email]
        return jsonify({'error': 'OTP expired. Please request a new one.'}), 400

    # Verify OTP matches
    if otp_data['otp'] != otp:
        return jsonify({'error': 'Invalid OTP. Please try again.'}), 400

    # Find user and update password
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Update password
    user.password_hash = hash_password(new_password)
    db.session.commit()

    # Clear OTP from store
    del otp_store[email]

    return jsonify({
        'success': True,
        'message': 'Password reset successful! You can now login.'
    }), 200


@app.route('/')
def index():
    """Serves the main dashboard HTML."""
    return render_template('index.html')

@app.route('/complete-profile')
def complete_profile():
    """Serves the Complete Your Profile page."""
    return render_template('complete_profile.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serves uploaded resumes."""
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/stream-jobs/<int:user_id>')
def stream_jobs(user_id):
    """Server-Sent Events endpoint for real-time job streaming."""
    def event_stream():
        state = scraping_state.get(user_id)
        if not state:
            yield f"data: {json.dumps({'type': 'error', 'data': {'message': 'No scraping session found'}})}\n\n"
            return

        # Send initial state immediately
        yield f"data: {json.dumps({
            'type': 'init',
            'data': {
                'jobs': state['jobs'],
                'scraping': state['scraping'],
                'processed_skills': state.get('processed_skills', 0),
                'total_skills': state.get('total_skills', 0),
                'total_jobs': len(state['jobs'])
            }
        })}\n\n"

        # Stream new jobs as they come in
        while not state.get('finished', False):
            try:
                message = state['queue'].get(timeout=5)  # 5 second timeout
                yield f"data: {json.dumps(message)}\n\n"
            except Empty:
                # Timeout - send heartbeat
                yield f": heartbeat\n\n"
                continue
            except GeneratorExit:
                break
    
    return Response(event_stream(), mimetype='text/event-stream')

@app.route('/get-jobs/<int:user_id>')
def get_jobs(user_id):
    """Get all jobs for a user from database OR live scraping state."""
    print(f"📊 Fetching jobs for user {user_id}...")
    
    # First try to get from live scraping state
    state = scraping_state.get(user_id)
    if state and len(state['jobs']) > 0:
        print(f"   ✅ Found {len(state['jobs'])} jobs in live scraping state")
        return jsonify({
            'jobs': state['jobs'],
            'total': len(state['jobs']),
            'source': 'live_state'
        })
    
    # Fallback to database
    jobs = JobMatch.query.filter_by(user_id=user_id).order_by(JobMatch.relevance_score.desc()).all()
    print(f"   📁 Found {len(jobs)} jobs in database")
    
    jobs_data = [{
        'id': job.id,
        'title': job.title,
        'company': job.company,
        'url': job.url,
        'source': job.source,
        'job_type': job.job_type,
        'relevance_score': job.relevance_score,
        'salary': job.salary or 'Not specified',
        'location': job.location or 'Remote',
        'description': job.description or '',
        'job_function': job.job_function or '',
        'expiry_date': job.expiry_date or '',
        'skills': [s.strip() for s in job.skills_required.split(',')] if job.skills_required else [],
        'region': job.region or 'India',
        'stateOrContinent': job.state_or_continent or 'All',
        'type': [job.job_type] if job.job_type else ['Full Time']
    } for job in jobs]
    
    return jsonify({
        'jobs': jobs_data,
        'total': len(jobs_data),
        'source': 'database'
    })

@app.route('/debug-jobs/<int:user_id>')
def debug_jobs(user_id):
    """Debug endpoint to check jobs in database."""
    jobs = JobMatch.query.filter_by(user_id=user_id).all()
    state = scraping_state.get(user_id)
    
    return jsonify({
        'user_id': user_id,
        'jobs_in_db': len(jobs),
        'jobs_in_state': len(state['jobs']) if state else 0,
        'scraping': state['scraping'] if state else False,
        'finished': state['finished'] if state else False,
        'sample_jobs': [{
            'title': j.title,
            'source': j.source,
            'score': j.relevance_score
        } for j in jobs[:5]]
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handles resume upload, starts background scraping, redirects to profile page."""
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
    experience_level = request.form.get('experience_level', '')
    preferred_location = request.form.get('preferred_location', '')

    # Phase 1: Save User to SQLite Database
    # Check if user already exists (avoid duplicate email constraint error)
    email = user_profile.get('email', '').strip().lower()
    user = User.query.filter_by(email=email).first()

    if user:
        # Update existing user's profile
        user.name = user_profile.get('name', 'Applicant')
        user.phone = user_profile.get('phone', '')
        user.level = user_profile['level']
        user.skills = ", ".join(user_profile['skills'])
        user.job_role = user_profile.get('job_role', '')
        print(f"🔄 Updated existing user: {email}")
    else:
        # Create new user
        user = User(
            name=user_profile.get('name', 'Applicant'),
            email=email,
            phone=user_profile.get('phone', ''),
            level=user_profile['level'],
            skills=", ".join(user_profile['skills']),
            job_role=user_profile.get('job_role', ''),
            password_hash=hash_password("resume-upload-user")
        )
        db.session.add(user)
        print(f"✅ Created new user: {email}")

    db.session.commit()

    # Initialize scraping state for this user but DO NOT start scraping yet
    scraping_state[user.id] = {
        'jobs': [],
        'scraping': False,
        'finished': False,
        'queue': Queue(),
        'total_skills': len(user_profile['skills']),
        'processed_skills': 0
    }

    # Return profile data and redirect info
    return jsonify({
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "level": user.level,
        "skills": user_profile['skills'],
        "job_type": job_type,
        "experience_level": experience_level,
        "preferred_location": preferred_location,
        "resume_url": f"/uploads/{file.filename}",
        "redirect": "/complete-profile"
    })

@app.route('/start-scraping', methods=['POST'])
def start_scraping():
    """Triggered by the user to start background scraping after resume upload."""
    data = request.json
    user_id = data.get('user_id')
    job_type = data.get('job_type', 'Full-time')
    experience_level = data.get('experience_level', '')
    preferred_location = data.get('preferred_location', '')

    # Normalize job type for the scraper ("Full Time" -> "Full-time")
    if job_type == "Full Time":
        job_type = "Full-time"
    elif job_type == "Part Time":
        job_type = "Part-time"

    if not user_id:
        return jsonify({"error": "User ID required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Delete old jobs for this user to avoid confusion and duplication
    try:
        JobMatch.query.filter_by(user_id=user.id).delete()
        db.session.commit()
        print(f"🧹 Cleared old jobs for user {user.id}")
    except Exception as e:
        print(f"⚠ Error clearing old jobs: {e}")
        db.session.rollback()

    # Re-initialize scraping state just in case it was modified
    skills_list = [s.strip() for s in user.skills.split(',') if s.strip()]
    
    scraping_state[user.id] = {
        'jobs': [],
        'scraping': True,
        'finished': False,
        'queue': Queue(),
        'total_skills': len(skills_list),
        'processed_skills': 0
    }

    # Start background scraping
    scrape_thread = threading.Thread(
        target=background_scrape_job,
        args=(user.id, skills_list, user.level, 
              job_type, experience_level if experience_level else user.level,
              preferred_location, user.job_role),
        daemon=True
    )
    scrape_thread.start()

    return jsonify({"success": True, "message": "Scraping started"})

@app.route('/update-profile', methods=['POST'])
def update_profile():
    """Update user profile with completed information."""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID required"}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Update user fields
    if 'name' in data:
        user.name = data['name']
    if 'email' in data:
        user.email = data['email']
    if 'job_type' in data:
        user.job_type = data['job_type']
    if 'location' in data:
        user.location = data['location']
    if 'job_role' in data:
        user.job_role = data['job_role']
    
    db.session.commit()
    
    return jsonify({
        "success": True,
        "user_id": user.id,
        "name": user.name
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

@app.route('/dashboard')
def dashboard():
    """Serves the new dashboard page for authenticated users."""
    return render_template('dashboard.html')

@app.route('/api/receive-n8n-jobs', methods=['POST'])
def receive_n8n_jobs():
    data = request.json
    
    # Check if this is an array of jobs or a single job
    if isinstance(data, list):
        jobs_data = data
    else:
        jobs_data = [data]
        
    for job_item in jobs_data:
        # Check if Ollama wrapped it in 'content' with markdown JSON string
        if 'content' in job_item and isinstance(job_item['content'], str):
            try:
                import json
                import re
                # Try to extract JSON from markdown code blocks if present
                content_str = job_item['content']
                match = re.search(r'```(?:json)?\n(.*?)\n```', content_str, re.DOTALL)
                if match:
                    parsed_content = json.loads(match.group(1))
                else:
                    parsed_content = json.loads(content_str)
                    
                # Merge parsed content into the job_item, prioritizing parsed fields
                job_item.update(parsed_content)
            except Exception as e:
                print(f"⚠️ Failed to parse n8n content block: {e}")
                pass # Proceed with what we have
    
        user_id = job_item.get('user_id')
        if not user_id:
            # Fallback to session if available, or just use 1 for testing if needed
            user_id = session.get('user_id', 1) 
            
        user = db.session.get(User, user_id)
        
        if not user:
            print(f"⚠️ User {user_id} not found for n8n job")
            continue

        # Robust field mapping (n8n might send job_title instead of title)
        title = job_item.get('title') or job_item.get('job_title', 'N/A')
        company = job_item.get('company') or 'N/A'
        
        raw_url = job_item.get('url') or job_item.get('link') or '#'
        
        # Ensure URL is absolute to prevent frontend 404s
        if raw_url != '#' and not raw_url.startswith(('http://', 'https://')):
            # Sometimes n8n sends markdown links like [https://...](https://...)
            import re
            md_match = re.search(r'\]\((.*?)\)', raw_url)
            if md_match:
                url = md_match.group(1)
            elif raw_url.startswith('www.'):
                url = 'https://' + raw_url
            else:
                url = 'https://' + raw_url
        else:
            url = raw_url
            
        # Also clean up markdown URLs if they snuck in with http prefix
        if url.startswith('http') and '](' in url:
            import re
            md_match = re.search(r'\]\((.*?)\)', url)
            if md_match:
                url = md_match.group(1)

        skills_list = job_item.get('skills', [])
        if isinstance(skills_list, list):
            skills_str = ', '.join(skills_list)
        else:
            skills_str = str(skills_list)

        # Create the new job match
        new_job = JobMatch(
            user_id=user_id,
            title=title,
            company=company,
            url=url,
            source=job_item.get('source', 'n8n Scraper'),
            relevance_score=job_item.get('relevance_score', 80),
            salary=job_item.get('salary', 'Not specified'),
            location=job_item.get('location', 'Remote'),
            description=job_item.get('description', ''),
            skills_required=skills_str,
            region=job_item.get('region', 'India'),
            state_or_continent=job_item.get('state_or_continent', 'All')
        )
        
        db.session.add(new_job)
        db.session.commit()
        print(f"✅ Saved new n8n job to DB: {new_job.title} at {new_job.company}")
        
        # Update SSE queue if available so UI refreshes
        state = scraping_state.get(user_id)
        if state and 'queue' in state:
            state['jobs'].append({
                'id': new_job.id,
                'title': new_job.title,
                'company': new_job.company,
                'url': new_job.url,
                'source': new_job.source,
                'description': new_job.description,
                'job_function': new_job.job_function,
                'expiry_date': new_job.expiry_date,
                'relevance_score': new_job.relevance_score
            })
            state['queue'].put({
                'type': 'job',
                'data': state['jobs'][-1],
                'total_jobs': len(state['jobs'])
            })
    
    return jsonify({"success": True}), 200

@app.route('/api/jobs-by-role/<int:user_id>')
def api_jobs_by_role(user_id):
    """Get jobs for a user filtered by role keyword."""
    role = request.args.get('role', '').strip()
    print(f"📋 Fetching jobs for user {user_id}, role filter: '{role}'")

    query = JobMatch.query.filter_by(user_id=user_id)
    if role:
        # Filter jobs whose title contains the role keyword (case-insensitive)
        query = query.filter(JobMatch.title.ilike(f'%{role}%'))

    jobs = query.order_by(JobMatch.relevance_score.desc()).all()
    print(f"   📁 Found {len(jobs)} jobs matching role '{role}'")

    jobs_data = [{
        'id': job.id,
        'title': job.title,
        'company': job.company,
        'url': job.url,
        'source': job.source,
        'job_type': job.job_type,
        'relevance_score': job.relevance_score,
        'saved': job.saved,
        'salary': job.salary or 'Not specified',
        'location': job.location or 'Remote',
        'description': job.description or '',
        'job_function': job.job_function or '',
        'expiry_date': job.expiry_date or '',
        'skills': [s.strip() for s in job.skills_required.split(',')] if job.skills_required else [],
        'region': job.region or 'India',
        'stateOrContinent': job.state_or_continent or 'All',
        'type': [job.job_type] if job.job_type else ['Full Time']
    } for job in jobs]

    return jsonify({'jobs': jobs_data, 'total': len(jobs_data)})


@app.route('/api/all-jobs/<int:user_id>')
def api_all_jobs(user_id):
    """Get ALL jobs for a user (grouped by role tabs)."""
    print(f"📋 Fetching all jobs for user {user_id}")

    jobs = JobMatch.query.filter_by(user_id=user_id).order_by(JobMatch.relevance_score.desc()).all()

    # Extract unique role keywords from job titles
    role_keywords = []
    seen_keywords = set()
    for job in jobs:
        # Use first 3 words of title as potential role keyword
        words = job.title.split()[:3]
        keyword = ' '.join(words)
        if keyword.lower() not in seen_keywords:
            seen_keywords.add(keyword.lower())
            role_keywords.append(keyword)

    jobs_data = [{
        'id': job.id,
        'title': job.title,
        'company': job.company,
        'url': job.url,
        'source': job.source,
        'job_type': job.job_type,
        'relevance_score': job.relevance_score,
        'saved': job.saved,
        'salary': job.salary or 'Not specified',
        'location': job.location or 'Remote',
        'description': job.description or '',
        'job_function': job.job_function or '',
        'expiry_date': job.expiry_date or '',
        'skills': [s.strip() for s in job.skills_required.split(',')] if job.skills_required else [],
        'region': job.region or 'India',
        'stateOrContinent': job.state_or_continent or 'All',
        'type': [job.job_type] if job.job_type else ['Full Time']
    } for job in jobs]

    return jsonify({
        'jobs': jobs_data,
        'roles': role_keywords[:10],  # Limit to 10 tabs
        'total': len(jobs_data)
    })


@app.route('/api/toggle-save-job', methods=['POST'])
def api_toggle_save_job():
    """Save or unsave a job."""
    data = request.get_json()
    job_id = data.get('job_id')
    user_id = data.get('user_id')

    if not job_id or not user_id:
        return jsonify({'error': 'job_id and user_id required'}), 400

    job = JobMatch.query.filter_by(id=job_id, user_id=user_id).first()
    if not job:
        return jsonify({'error': 'Job not found'}), 404

    job.saved = not job.saved
    db.session.commit()

    return jsonify({'saved': job.saved, 'job_id': job.id})


@app.route('/api/saved-jobs/<int:user_id>')
def api_saved_jobs(user_id):
    """Get all saved (bookmarked) jobs for a user."""
    jobs = JobMatch.query.filter_by(user_id=user_id, saved=True).order_by(JobMatch.relevance_score.desc()).all()

    jobs_data = [{
        'id': job.id,
        'title': job.title,
        'company': job.company,
        'url': job.url,
        'source': job.source,
        'job_type': job.job_type,
        'relevance_score': job.relevance_score,
        'salary': job.salary or 'Not specified',
        'location': job.location or 'Remote',
        'description': job.description or '',
        'job_function': job.job_function or '',
        'expiry_date': job.expiry_date or '',
        'skills': [s.strip() for s in job.skills_required.split(',')] if job.skills_required else [],
        'region': job.region or 'India',
        'stateOrContinent': job.state_or_continent or 'All',
        'type': [job.job_type] if job.job_type else ['Full Time']
    } for job in jobs]

    return jsonify({'jobs': jobs_data, 'total': len(jobs_data)})


@app.route('/api/applications/<int:user_id>')
def api_applications(user_id):
    """Get all applications for a user with job details."""
    applications = Application.query.filter_by(user_id=user_id).all()

    apps_data = []
    for app in applications:
        job = JobMatch.query.get(app.job_id)
        if job:
            apps_data.append({
                'id': app.id,
                'job_id': app.job_id,
                'title': job.title,
                'company': job.company,
                'url': job.url,
                'source': job.source,
                'status': app.status,
                'applied_date': app.applied_date.isoformat() if app.applied_date else None
            })

    return jsonify({'applications': apps_data, 'total': len(apps_data)})


@app.route('/api/application', methods=['POST'])
def api_create_update_application():
    """Create or update an application (add to tracking)."""
    data = request.get_json()
    user_id = data.get('user_id')
    job_id = data.get('job_id')
    status = data.get('status', 'Applied')

    if not user_id or not job_id:
        return jsonify({'error': 'user_id and job_id required'}), 400

    # Check if application already exists
    existing = Application.query.filter_by(user_id=user_id, job_id=job_id).first()
    if existing:
        existing.status = status
        db.session.commit()
        return jsonify({'success': True, 'application_id': existing.id, 'status': status})

    new_app = Application(user_id=user_id, job_id=job_id, status=status)
    db.session.add(new_app)
    db.session.commit()

    return jsonify({'success': True, 'application_id': new_app.id, 'status': status})


@app.route('/api/update-application-status', methods=['POST'])
def api_update_application_status():
    """Update the status of an existing application."""
    data = request.get_json()
    app_id = data.get('application_id')
    status = data.get('status')

    if not app_id or not status:
        return jsonify({'error': 'application_id and status required'}), 400

    application = Application.query.get(app_id)
    if not application:
        return jsonify({'error': 'Application not found'}), 404

    application.status = status
    db.session.commit()

    return jsonify({'success': True, 'application_id': app_id, 'status': status})


@app.route('/api/skillup/<int:user_id>')
def api_skillup(user_id):
    """Get skill gap analysis for a user."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    user_skills = set()
    if user.skills:
        user_skills = set(s.strip().lower() for s in user.skills.split(',') if s.strip())

    # Get all job titles for this user to find commonly required skills
    jobs = JobMatch.query.filter_by(user_id=user_id).all()

    # Simple skill gap: common tech skills that appear in job titles but not in user profile
    common_skills = {
        'python', 'javascript', 'react', 'node', 'aws', 'docker', 'kubernetes',
        'sql', 'git', 'linux', 'html', 'css', 'java', 'go', 'rust',
        'tensorflow', 'pytorch', 'pandas', 'numpy', 'mongodb', 'postgresql',
        'mysql', 'redis', 'graphql', 'typescript', 'vue', 'angular',
        'figma', 'adobe photoshop', 'agile', 'scrum', 'jenkins', 'terraform',
        'ansible', 'elasticsearch', 'kafka', 'rabbitmq', 'nginx'
    }

    # Find skills in job titles not in user profile
    missing_skills = []
    for job in jobs:
        title_lower = job.title.lower()
        for skill in common_skills:
            if skill in title_lower and skill not in user_skills:
                missing_skills.append(skill)

    # Deduplicate
    missing_skills = list(set(missing_skills))

    # Recommended resources (static for now)
    resources = {
        'python': {'name': 'Python for Everybody', 'url': 'https://www.py4e.com/'},
        'javascript': {'name': 'JavaScript.info', 'url': 'https://javascript.info/'},
        'react': {'name': 'React Official Tutorial', 'url': 'https://react.dev/learn'},
        'node': {'name': 'Node.js Official Guide', 'url': 'https://nodejs.org/en/learn'},
        'aws': {'name': 'AWS Free Tier Training', 'url': 'https://aws.amazon.com/free/'},
        'docker': {'name': 'Docker Getting Started', 'url': 'https://docs.docker.com/get-started/'},
        'kubernetes': {'name': 'Kubernetes Basics', 'url': 'https://kubernetes.io/docs/tutorials/kubernetes-basics/'},
        'sql': {'name': 'SQLBolt', 'url': 'https://sqlbolt.com/'},
        'git': {'name': 'Git Handbook', 'url': 'https://docs.github.com/en/get-started'},
        'linux': {'name': 'Linux Journey', 'url': 'https://linuxjourney.com/'},
        'html': {'name': 'MDN HTML Guide', 'url': 'https://developer.mozilla.org/en-US/docs/Web/HTML'},
        'css': {'name': 'MDN CSS Guide', 'url': 'https://developer.mozilla.org/en-US/docs/Web/CSS'},
        'java': {'name': 'Java Tutorials (Oracle)', 'url': 'https://docs.oracle.com/javase/tutorial/'},
        'go': {'name': 'Go by Example', 'url': 'https://gobyexample.com/'},
        'rust': {'name': 'The Rust Book', 'url': 'https://doc.rust-lang.org/book/'},
        'tensorflow': {'name': 'TensorFlow Tutorials', 'url': 'https://www.tensorflow.org/tutorials'},
        'mongodb': {'name': 'MongoDB University', 'url': 'https://university.mongodb.com/'},
        'postgresql': {'name': 'PostgreSQL Tutorial', 'url': 'https://www.postgresqltutorial.com/'},
        'typescript': {'name': 'TypeScript Handbook', 'url': 'https://www.typescriptlang.org/docs/'},
        'vue': {'name': 'Vue.js Guide', 'url': 'https://vuejs.org/guide/'},
        'angular': {'name': 'Angular Tutorial', 'url': 'https://angular.io/start'},
        'figma': {'name': 'Figma Tutorial', 'url': 'https://www.figma.com/resources/learn-design/'},
        'agile': {'name': 'Agile Manifesto', 'url': 'https://agilemanifesto.org/'},
        'jenkins': {'name': 'Jenkins Getting Started', 'url': 'https://www.jenkins.io/doc/'},
        'terraform': {'name': 'Terraform Learn', 'url': 'https://learn.hashicorp.com/terraform'},
        'graphql': {'name': 'GraphQL Tutorial', 'url': 'https://graphql.org/learn/'},
        'redis': {'name': 'Redis Quick Start', 'url': 'https://redis.io/docs/latest/get-started/'},
        'nginx': {'name': 'Nginx Beginner Guide', 'url': 'https://nginx.org/en/docs/beginners_guide.html'},
        'kafka': {'name': 'Kafka Quickstart', 'url': 'https://kafka.apache.org/quickstart'},
    }

    skillup_items = []
    for skill in missing_skills[:15]:  # Top 15 missing skills
        resource = resources.get(skill, {'name': f'Learn {skill.title()}', 'url': f'https://www.google.com/search?q=learn+{skill}+tutorial'})
        skillup_items.append({
            'skill': skill.title(),
            'resource_name': resource['name'],
            'resource_url': resource['url']
        })

    return jsonify({
        'user_skills': list(user_skills),
        'missing_skills': skillup_items,
        'total_missing': len(skillup_items)
    })


@app.route('/api/update-profile-preferences', methods=['POST'])
def api_update_profile_preferences():
    """Update all profile fields from the dashboard profile section."""
    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({'error': 'user_id required'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if 'name' in data:
        user.name = data['name']
    if 'email' in data:
        user.email = data['email']
    if 'job_role' in data:
        user.job_role = data['job_role']
    if 'job_type' in data:
        user.job_type = data['job_type']
    if 'location' in data:
        user.location = data['location']

    if 'skills' in data:
        user.skills = data['skills']
        
    if 'about' in data: user.about = data['about']
    if 'projects' in data: user.projects = data['projects']
    if 'achievements' in data: user.achievements = data['achievements']
    if 'education' in data: user.education = data['education']
    if 'certificates' in data: user.certificates = data['certificates']
    if 'positions_of_responsibility' in data: user.positions_of_responsibility = data['positions_of_responsibility']
    
    if 'social' in data and data['social']:
        social = data['social']
        if 'github' in social: user.social_github = social['github']
        if 'linkedIn' in social: user.social_linkedin = social['linkedIn']
        if 'portfolio' in social: user.social_portfolio = social['portfolio']
        
    if 'photoDataUrl' in data: user.photo_data_url = data['photoDataUrl']


    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Profile updated successfully',
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'job_role': user.job_role,
            'job_type': user.job_type,
            'location': user.location,
            'skills': user.skills
        }
    })


if __name__ == '__main__':
    app.run(debug=True, threaded=True)
