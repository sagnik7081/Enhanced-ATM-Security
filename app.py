from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash, send_from_directory
import os
import sqlite3
import hashlib
from functools import wraps
import time
import shutil

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this in production

# Constants
DB_PATH = "face_auth.db"
AUTHORIZED_DIR = "authorized_faces"
BANNED_DIR = "banned_faces"
UNAUTHORIZED_DIR = "unauthorized_faces"

# Create directories if not exist
for folder in [AUTHORIZED_DIR, BANNED_DIR, UNAUTHORIZED_DIR]:
    os.makedirs(folder, exist_ok=True)

# Database initialization
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create users table for face recognition
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            face_id TEXT UNIQUE,
            attempts INTEGER DEFAULT 0,
            authorized INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create admin users table for web login
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT
        )
    """)
    
    # Check if default admin exists
    cursor.execute("SELECT * FROM admins WHERE username = 'admin'")
    if not cursor.fetchone():
        # Create default admin (username: admin, password: admin123)
        # Make sure we're using the same hashing method as in the login function
        password = "admin123"
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        print(f"Creating default admin with hash: {hashed_password}")
        
        cursor.execute("INSERT INTO admins (username, password, email) VALUES (?, ?, ?)",
                      ("admin", hashed_password, "admin@example.com"))
    
    conn.commit()
    conn.close()

# Reset admin password for testing purposes
def reset_admin():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    password = "admin123"
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    print(f"Resetting admin password with hash: {hashed_password}")
    
    cursor.execute("UPDATE admins SET password = ? WHERE username = 'admin'", (hashed_password,))
    
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# Uncomment the line below to reset the admin password if needed
# reset_admin()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Debug output
        print(f"Login attempt: {username}")
        print(f"Hashed password: {hashed_password}")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM admins WHERE username = ?", (username,))
            user = cursor.fetchone()
            
            if user:
                print(f"Found user: {user}")
                stored_password = user[2]  # password is at index 2
                print(f"Stored password hash: {stored_password}")
                print(f"Input password hash: {hashed_password}")
                
                if stored_password == hashed_password:
                    session['username'] = username
                    conn.close()  # Ensure connection is always closed
                    return redirect(url_for('dashboard'))
            
            error = 'Invalid credentials. Please try again.'
        finally:
            conn.close()  # Ensure connection is always closed
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/requests')
@login_required
def get_requests():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT face_id, timestamp, authorized FROM users 
        ORDER BY timestamp DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    requests = []
    for row in rows:
        face_id, timestamp, status = row
        face_image = None
        
        # Check which directory the face is in
        if status == 1:
            directory = AUTHORIZED_DIR
            status_text = "Authorized"
        elif status == -1:
            directory = BANNED_DIR
            status_text = "Banned"
        else:
            directory = UNAUTHORIZED_DIR
            status_text = "Pending"
            
        image_path = os.path.join(directory, f"{face_id}.jpg")
        if os.path.exists(image_path):
            face_image = f"/faces/{directory}/{face_id}.jpg"
        
        requests.append({
            'face_id': face_id,
            'timestamp': timestamp,
            'status': status_text,
            'status_code': status,
            'image': face_image or "/static/img/no-image.png"
        })
    
    return jsonify(requests)

@app.route('/api/approve/<face_id>')
@login_required
def approve_user(face_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET authorized = 1 WHERE face_id = ?", (face_id,))
    conn.commit()
    conn.close()
    
    # Move image from unauthorized to authorized
    src_path = os.path.join(UNAUTHORIZED_DIR, f"{face_id}.jpg")
    dest_path = os.path.join(AUTHORIZED_DIR, f"{face_id}.jpg")
    
    if os.path.exists(src_path):
        shutil.copy2(src_path, dest_path)  # Copy the file
    
    return jsonify({'success': True, 'message': f'User {face_id} approved'})

@app.route('/api/ban/<face_id>')
@login_required
def ban_user(face_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET authorized = -1 WHERE face_id = ?", (face_id,))
    conn.commit()
    conn.close()
    
    # Move image from unauthorized to banned
    src_path = os.path.join(UNAUTHORIZED_DIR, f"{face_id}.jpg")
    dest_path = os.path.join(BANNED_DIR, f"{face_id}.jpg")
    
    if os.path.exists(src_path):
        shutil.copy2(src_path, dest_path)  # Copy the file
    
    return jsonify({'success': True, 'message': f'User {face_id} banned'})

# Serve face images
@app.route('/faces/<directory>/<filename>')
@login_required
def serve_face(directory, filename):
    return send_from_directory(directory, filename)

# New API endpoints for face recognition system
@app.route('/api/alerts/new', methods=['POST'])
def register_alert():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
        
    data = request.json
    face_id = data.get('face_id')
    
    if not face_id:
        return jsonify({"error": "face_id is required"}), 400
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # Insert the new face detection into the database
        cursor.execute("""
            INSERT INTO users (face_id, authorized) 
            VALUES (?, 0) 
            ON CONFLICT(face_id) DO UPDATE SET 
            timestamp=CURRENT_TIMESTAMP, attempts=attempts+1
        """, (face_id,))
        conn.commit()
        
        return jsonify({
            "success": True,
            "message": f"Alert registered for {face_id}",
            "face_id": face_id
        })
    except Exception as e:
        print(f"Error registering alert: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/status/<face_id>')
def check_status(face_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT authorized FROM users WHERE face_id = ?", (face_id,))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({"status": "unknown", "face_id": face_id})
        
        status_code = result[0]
        
        if status_code == 1:
            status = "approved"
        elif status_code == -1:
            status = "banned"
        else:
            status = "pending"
            
        return jsonify({
            "status": status,
            "face_id": face_id
        })
    except Exception as e:
        print(f"Error checking status: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)