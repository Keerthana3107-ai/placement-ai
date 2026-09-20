# AI-Powered Placement Management System

A practical, modern, responsive full-stack college placement management platform built with **Python, Flask, SQLite, SQLAlchemy, Scikit-learn, Chart.js, and Bootstrap 5**.

## 🚀 Live Demo

👉 **[Open Placement AI](https://placement-ai-wzdk.onrender.com)**

> The live application is deployed on Render.

---

## 🌟 Key Features

### 🎓 1. Student Portal
* **Personal & Academic Profile:** Multi-section profile managing personal details, 10th/12th percentages, CGPA, department, graduation year, technical skills with proficiency tags, portfolio projects, and verified certifications.
* **Profile Completion Meter:** Real-time calculation with progress indicator and tailored tips (Personal 20%, Academic 20%, Skills 20%, Projects 20%, Certifications 10%, Resume 10%).
* **AI-Powered Job Recommendations:** Personalized job ranking based on Scikit-Learn TF-IDF vector similarity and deterministic academic heuristics with transparent explanations ("Why this job matches you").
* **Automated Eligibility Checker:** Real-time checking of CGPA cutoff, eligible branch, graduation year, and required skills. Blocks ineligible candidates with clear itemized explanations.
* **Application Tracker:** Visual status timeline (*Applied → Under Review → Shortlisted → Interview Scheduled → Selected / Rejected*).
* **Live Interview Countdown:** Real-time JavaScript countdown timer to the next scheduled interview round, with direct video meeting links.
* **In-App Notification Center:** Unread badge in header with dropdown and 1-click mark-as-read.

### 📄 2. AI Resume Skill Analyzer
* Upload PDF resumes with drag-and-drop support.
* Extracts text safely using `pypdf` / `PyPDF2` with regex-based NLP matching across 70+ industry technologies (Python, Java, React, SQL, Flask, Machine Learning, Docker, AWS, etc.).
* Displays detected skills with checkmarks and provides 1-click automatic import into the student's profile.

### 🏛️ 3. Placement Officer / Admin Dashboard
* **6 Key Performance Indicators:** Total Students, Total Companies, Active Jobs, Total Applications, Placed Count, Placement Percentage.
* **5 Interactive Chart.js Visualizations:**
  1. Applications by Recruiting Company (Bar Chart)
  2. Placement Status Ratio: Placed vs Unplaced vs Opted Out (Doughnut Chart)
  3. Branch-wise Placed vs Unplaced (Stacked Bar Chart)
  4. Monthly/Weekly Application Trends (Smooth Line Chart)
  5. Salary / CTC Package Distribution (Bar Chart)
* **Company & Job Management:** Full CRUD for corporate partners and campus drives.
* **Student Directory:** Searchable roster with branch, CGPA, and placement filters, plus resume downloading and placement status updating.
* **Master Application Roster:** Filter by drive and update applicant statuses in real-time.
* **Interview Coordination:** Schedule interview rounds, set dates/times, and attach meeting URLs with automatic student notification.
* **Report Export:** 1-Click CSV export of complete university placement records.

### 💼 4. Company / Recruiter Portal
* **Recruiter Dashboard:** Overview of active drives, candidate pipeline, shortlisted applicants, interviews, and hires.
* **Post & Edit Job Drives:** Configure minimum CGPA cutoffs, allowed engineering disciplines, graduation batch, CTC, openings, and skill criteria.
* **Applicant Pipeline with AI Match Scores:** View applicants ranked by AI compatibility, inspect resumes, change candidate status, and schedule interview rounds.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons, Chart.js 4.4 |
| **Backend** | Python 3, Flask, REST API architecture, Werkzeug |
| **Database** | SQLite, SQLAlchemy ORM |
| **AI / Machine Learning** | Scikit-learn (TfidfVectorizer, Cosine Similarity), Joblib, PyPDF / Regex NLP |

*Zero external paid APIs required. 100% self-contained local operation.*

---

## 🚀 Quick Start Guide

### Step 1: Install Dependencies
Open your command prompt or terminal in the project directory:
```bash
cd C:\Users\Admin\.gemini\antigravity\scratch\placement_portal
pip install -r requirements.txt
```

### Step 2: Seed Database with Realistic Demo Data
Run the seeding script to initialize the SQLite database with companies (Google, Microsoft, Amazon, TCS, Infosys, Deloitte), diverse student profiles, active job drives, applications, and scheduled interviews:
```bash
python seed.py
```

### Step 3: Start the Web Application
```bash
python app.py
```

### Step 4: Open in Your Web Browser
Navigate to:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🔑 Pre-Configured Demo Credentials

You can log in manually or use the **1-Click Quick Demo Login** buttons right on the login page:

| Role | Email / Identifier | Password | Description |
|---|---|---|---|
| **Student** | `student@example.com` | `password123` | Alex Morgan (Computer Science, 8.85 CGPA, Full Skills & Projects) |
| **Placement Officer / Admin** | `admin@example.com` | `admin123` | University Placement Cell Administrator |
| **Company / Recruiter** | `recruiter@google.com` | `password123` | Google Campus Recruitment Lead |
| **Company / Recruiter** | `recruiter@microsoft.com` | `password123` | Microsoft Talent Acquisition |
| **Company / Recruiter** | `recruiter@amazon.com` | `password123` | Amazon SDE Recruiter |

---

## 📂 Project Directory Structure

```
placement_portal/
├── app.py                      # Flask Application Factory & Entry Point
├── config.py                   # App Configuration & Upload Paths
├── models.py                   # SQLAlchemy Database Schema (User, Job, Student, etc.)
├── seed.py                     # Rich Demo Data Populator
├── requirements.txt            # Python Dependencies
├── README.md                   # Complete Documentation
├── ai_engine/
│   ├── __init__.py
│   ├── recommender.py          # Scikit-Learn TF-IDF Matching & Explainability Model
│   └── resume_parser.py        # PDF Resume Text & Skill Extractor
├── routes/
│   ├── __init__.py
│   ├── auth.py                 # Authentication & Role Decorators
│   ├── student.py              # Student Dashboard, Profile, Drives & Timeline
│   ├── admin.py                # Admin Analytics, CRUD, CSV Export
│   ├── company.py              # Recruiter Job Postings & Pipeline
│   └── api.py                  # Dynamic REST Endpoints (Eligibility, Charts, Notifs)
├── static/
│   ├── css/
│   │   ├── style.css           # Custom Modern Design, Glassmorphism, Timeline Stepper
│   │   └── dashboard.css       # Utility Dashboard Styles
│   └── js/
│       ├── main.js             # Notifications, Drawer, Interview Countdown
│       ├── charts.js           # Chart.js Renderers for Admin & Student
│       ├── eligibility.js      # Dynamic Eligibility Modal Evaluator
│       └── resume_upload.js    # Drag-and-drop Resume Uploader
├── templates/
│   ├── base.html               # Master Layout with Responsive Sidebar & Topbar
│   ├── index.html              # Landing Page with Hero & 1-Click Demo Logins
│   ├── auth/
│   │   ├── login.html          # Clean Login with Demo Pills
│   │   └── register.html       # Role-Based Registration
│   ├── student/                # Student Dashboard, Profile, Drives, Applications, etc.
│   ├── admin/                  # Analytics Dashboard, Companies, Jobs, Students, etc.
│   ├── company/                # Recruiter Dashboard, Post Job, Pipeline, etc.
│   └── errors/                 # 404 & 500 Handlers
└── uploads/
    └── resumes/                # Uploaded Student PDF Storage
```
