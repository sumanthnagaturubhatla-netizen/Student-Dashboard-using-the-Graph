# Student Dashboard with Performance Graph 📊🎓

An interactive, full-stack Student Performance Tracking and Analytics Dashboard built with **Django**, **Chart.js**, and custom **JWT-based authentication**. It features student registration/login forms, administrative controls, attendance tracking, and dynamic visual graphs representing student progress.

---

## 🚀 Key Features

* **Visual Analytics Dashboard:** Dynamic line and bar graphs using **Chart.js** displaying student performance and scores over time.
* **Role-Based Portals:**
  * **Students:** Access personal performance metrics, average scores, profile details, and attendance rates.
  * **Administrators:** Manage student lists, edit student credentials, update academic records, and monitor system analytics.
* **Custom JWT Authentication:** Fully customized JSON Web Token (JWT) system (`jwt_utils.py`, `auth_middleware.py`) handling secure session validation, token refreshing, and blacklisting/whitelist verification.
* **Attendance Tracker:** Visual display and database logging of student attendance percentages (Present, Absent, Late).
* **Automated Setup & Recovery:** Includes diagnostic scripts and error-repair batches (`fix_errors.py`, `emergency_fix.py`, `verify_jwt_setup.py`) to verify system health and JWT consistency.

---

## 🛠️ Technology Stack

* **Backend:** Python, Django Web Framework
* **Authentication:** Custom JWT Middleware (Access & Refresh Tokens)
* **Frontend:** HTML5, CSS3 (Bootstrap, Custom Gradients), JavaScript, Chart.js, FontAwesome
* **Database:** SQLite

---

## ⚙️ Installation & Run Guide

### 1. Prerequisites
* Python 3.10+ installed

### 2. Setup Virtual Environment
In the root project folder:
```bash
# Set up virtual environment
python -m venv venv

# Activate on Windows
.\venv\Scripts\Activate.ps1

# Activate on macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
Ensure Django and PyJWT are installed (or run the custom setup batch):
```bash
pip install django PyJWT
```
*Alternatively, you can run:*
```bash
.\SETUP_JWT_QUICK.bat
```

### 4. Database Migrations
Create databases and initialize schemas:
```bash
python manage.py migrate
```

### 5. Start the Server
Run the helper script or the standard Django runserver:
```bash
# Via batch script
.\START_SERVER.bat

# Standard command
python manage.py runserver
```
Navigate to `http://127.0.0.1:8000` to view the application!

---

## 📝 Database Model Outline

* **Student:** Extended profile linking Django's auth model, including roll number, DOB, phone, and active status.
* **Performance:** Tracks academic scores (0-100) per subject (Mathematics, English, Science, History, Geography).
* **Attendance:** Daily records tracking attendance status (Present, Absent, Late).
* **RefreshToken:** Blacklist-compatible store verifying and managing issued JWT refresh tokens.
