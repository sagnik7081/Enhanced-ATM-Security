import smtplib
import os
from email.mime.text import MIMEText
from twilio.rest import Client
import sqlite3
from dotenv import load_dotenv

load_dotenv()

# Twilio Credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Email Credentials
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Database Path
DB_PATH = "face_auth.db"

def initialize_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        face_id TEXT PRIMARY KEY,
        authorized INTEGER DEFAULT 0,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()
    print("[INFO] Database initialized")

# Send email alert (without approval link)
def send_email(face_id, recipient_email):
    msg = MIMEText(f"🚨 Unauthorized access attempt detected at the ATM. Face ID: {face_id}")
    msg["Subject"] = "🚨 ATM Security Alert!"
    msg["From"] = EMAIL_SENDER
    msg["To"] = recipient_email

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, recipient_email, msg.as_string())
        server.quit()
        print("[INFO] Email sent successfully!")
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")
        raise  # 🚀 ADD THIS: Crash the app to SEE real error.


# Send SMS alert (without approval link)
def send_sms(face_id, recipient_phone):
    message = f"🚨 Alert! Unauthorized access attempt detected. Face ID: {face_id}"

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=recipient_phone
        )
        print("[INFO] SMS sent successfully!")
    except Exception as e:
        print(f"[ERROR] Failed to send SMS: {e}")
        raise  # 🚀 ADD THIS too


# Register a new unauthorized face in the database
def register_face(face_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (face_id) VALUES (?)", (face_id,))
    conn.commit()
    conn.close()

# Get approval status from database
def get_status(face_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT authorized FROM users WHERE face_id = ?", (face_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result is None:
        return None
    return "approved" if result[0] == 1 else "banned" if result[0] == -1 else "pending"

# Approve user
def approve_user(face_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET authorized = 1 WHERE face_id = ?", (face_id,))
    conn.commit()
    conn.close()
    print(f"[INFO] User {face_id} approved successfully!")

# Ban user
def ban_user(face_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET authorized = -1 WHERE face_id = ?", (face_id,))
    conn.commit()
    conn.close()
    print(f"[ALERT] User {face_id} has been banned!")

# Check if user is banned
def is_banned(face_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT authorized FROM users WHERE face_id = ?", (face_id,))
    result = cursor.fetchone()
    conn.close()
    return result and result[0] == -1

# Update detect.py integration
def register_new_alert(face_id):
    """Register a new unauthorized face and send notifications"""
    # Register in database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (face_id, authorized) VALUES (?, 0)", (face_id,))
    conn.commit()
    conn.close()
    
    # You can also send emails/SMS here if needed
    return True


# Initialize database when module is loaded
if __name__ == "__main__":
    initialize_database()
else:
    # Still initialize database when imported
    initialize_database()