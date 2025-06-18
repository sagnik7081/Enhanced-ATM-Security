# 🎪 ATM Security System with Facial Recognition 🚨🔒

<div align="center">

### 🎭 Welcome to the Most Fun Security System Ever! 🎭  
🤖 BEEP BOOP! DETECTING FACES! 🤖  
 ╔══════════════════╗  
 ║  👁️  WATCHING  👁️  ║  
 ║    YOU ALWAYS!    ║  
 ╚══════════════════╝  
      🔍 📸 🔍  

[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.0+-red?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org)
[![SQLite](https://img.shields.io/badge/SQLite-3.0+-orange?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)

</div>

---

## 🎨 Overview 📝

> 🎪 **Step right up!**  
> Welcome to the most entertaining ATM security system you've ever seen! This isn't just any ordinary facial recognition system — it's a **cartoon-powered, emoji-filled, super-fun security extravaganza!** 🎉

---

## ✨ Features That Will Make You Go WOW! ✨

| 🎭 Feature              | 🎪 Description                    | 🎨 Fun Factor      |
|------------------------|------------------------------------|--------------------|
| 📸 Face Detection       | insightface (buffalo_l) magic!     | 🌟🌟🌟🌟🌟           |
| 🎛️ Dashboard           | Approve/ban users like a boss!     | 🌟🌟🌟🌟            |
| 📧📱 Alerts             | Email & SMS notifications!         | 🌟🌟🌟             |
| 🗄️ Database            | SQLite storage wizardry!           | 🌟🌟🌟             |
| 🖼️ Preprocessing       | Image magic before detection!      | 🌟🌟              |
| 🌐 API                 | RESTful goodness!                  | 🌟🌟🌟             |

---

## 🗂️ Project Structure

```bash
atm-security-system/
├── app.py                 # Flask admin dashboard
├── detect.py              # Real-time detection and recognition
├── alerts.py              # Send email & SMS alerts
├── preprocess.py          # Align & clean face images
├── create_embeddings.py   # Generate ArcFace embeddings
├── embeddings.npz         # Saved 512D vectors of all users
├── face_auth.db           # SQLite DB for users & logs

├── dataset/
│   └── authorized/<name>/     # Authorized face images
│   └── unauthorized/          # Unauthorized face attempts

├── authorized_faces/      # Approved images
├── banned_faces/          # Disapproved images
├── processed_dataset/     # Preprocessed aligned images
├── debug_failed_faces/    # Debugging false/failed faces

├── templates/
│   ├── login.html         # Admin login page
│   └── dashboard.html     # Admin control panel

├── static/
│   ├── style.css          # Dark mode CSS
│   └── dashboard.js       # UI interactivity

├── .env                   # Email/Twilio credentials
├── requirements.txt       # All required packages
└── README.md              # This file

---

## 🛠️ Prerequisites (Your Toolkit!) 🛠️

| 🎭 Item       | 🎪 Version | 🎨 Purpose                  |
|--------------|------------|-----------------------------|
| 🐍 Python     | 3.8+       | The snake that runs it all! |
| 📷 Webcam     | Any        | Your window to the world!   |
| 📱 Twilio     | Account    | Your SMS superhero!         |
| 📧 Gmail      | App Pass   | Your email wizard!          |
| 🌐 Internet   | Stable     | Connection to the world!    |

---

## ⚙️ Installation (The Fun Setup!) ⚙️

# 1. Clone the repo
git clone https://github.com/sagnik7081/Enhanced-ATM-Security
cd Enhanced-Atm-Security

# 2. Setup virtual environment
python -m venv venv
venv\Scripts\activate       # On Windows
source venv/bin/activate    # On Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables (edit `.env`)
EMAIL_SENDER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
TWILIO_ACCOUNT_SID=xxxx
TWILIO_AUTH_TOKEN=xxxx
TWILIO_PHONE_NUMBER=+1234567890

# 5. Preprocess & embed
python preprocess.py
python create_embeddings.py

# 6. Launch the system
python app.py      # Run Flask dashboard
python detect.py   # Start real-time face detection



## 👥 Contributors (The Dream Team!)

- 🎭 **Sagnik7081** - The Mastermind! 🧠  
- 🎨 **Shaurya-2004** - The Artist! 🎨  
