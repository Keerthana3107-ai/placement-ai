from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # 'student', 'admin', 'company'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    student_profile = db.relationship('StudentProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    company_profile = db.relationship('Company', backref='user', uselist=False, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan', order_by='Notification.created_at.desc()')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    
    # Personal Info
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    department = db.Column(db.String(100), nullable=False, default='Computer Science')
    college = db.Column(db.String(150), nullable=False, default='Engineering Institute of Technology')
    graduation_year = db.Column(db.Integer, nullable=False, default=2026)
    
    # Academic Info
    cgpa = db.Column(db.Float, nullable=False, default=0.0)
    tenth_pct = db.Column(db.Float, nullable=True)
    twelfth_pct = db.Column(db.Float, nullable=True)
    
    # Resume & Placement
    resume_filename = db.Column(db.String(255), nullable=True)
    resume_extracted_text = db.Column(db.Text, nullable=True)
    placement_status = db.Column(db.String(50), default='Unplaced')  # 'Unplaced', 'Placed', 'Opted Out'
    placed_company = db.Column(db.String(100), nullable=True)
    placed_package = db.Column(db.Float, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    skills = db.relationship('Skill', backref='student', cascade='all, delete-orphan')
    projects = db.relationship('Project', backref='student', cascade='all, delete-orphan')
    certifications = db.relationship('Certification', backref='student', cascade='all, delete-orphan')
    applications = db.relationship('Application', backref='student', cascade='all, delete-orphan')
    interviews = db.relationship('Interview', backref='student', cascade='all, delete-orphan')

    def calculate_profile_completion(self):
        """
        Calculate profile completion:
        - Personal details: 20%
        - Academic details: 20%
        - Skills: 20%
        - Projects: 20%
        - Certifications: 10%
        - Resume: 10%
        """
        score = 0
        breakdown = {
            'personal': False,
            'academic': False,
            'skills': False,
            'projects': False,
            'certifications': False,
            'resume': False
        }
        suggestions = []

        # Personal details (20%)
        if self.full_name and self.phone and self.department and self.graduation_year:
            score += 20
            breakdown['personal'] = True
        else:
            suggestions.append("Complete personal details (phone number, department, graduation year)")

        # Academic details (20%)
        if self.cgpa and self.cgpa > 0 and (self.tenth_pct or self.twelfth_pct):
            score += 20
            breakdown['academic'] = True
        else:
            suggestions.append("Provide valid CGPA and 10th/12th percentages")

        # Skills (20%)
        if len(self.skills) >= 3:
            score += 20
            breakdown['skills'] = True
        elif len(self.skills) > 0:
            score += 10
            suggestions.append("Add at least 3 technical skills to enhance match score")
        else:
            suggestions.append("Add your key technical skills")

        # Projects (20%)
        if len(self.projects) >= 1:
            score += 20
            breakdown['projects'] = True
        else:
            suggestions.append("Add at least 1 academic or personal project")

        # Certifications (10%)
        if len(self.certifications) >= 1:
            score += 10
            breakdown['certifications'] = True
        else:
            suggestions.append("Add your industry certifications or courses")

        # Resume (10%)
        if self.resume_filename:
            score += 10
            breakdown['resume'] = True
        else:
            suggestions.append("Upload your latest PDF resume")

        return score, breakdown, suggestions

    def get_skill_names(self):
        return [s.skill_name.strip() for s in self.skills if s.skill_name]

    def __repr__(self):
        return f'<StudentProfile {self.full_name}>'


class Skill(db.Model):
    __tablename__ = 'skills'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    skill_name = db.Column(db.String(80), nullable=False)
    proficiency = db.Column(db.String(20), default='Intermediate')  # Beginner, Intermediate, Advanced
    
    def __repr__(self):
        return f'<Skill {self.skill_name}>'


class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    tech_stack = db.Column(db.String(255), nullable=True)  # e.g., "Python, Flask, SQLite"

    def __repr__(self):
        return f'<Project {self.title}>'


class Certification(db.Model):
    __tablename__ = 'certifications'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    issuer = db.Column(db.String(150), nullable=False)
    issue_year = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f'<Certification {self.title}>'


class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    logo_url = db.Column(db.String(255), nullable=True)
    industry = db.Column(db.String(100), nullable=False, default='Information Technology')
    location = db.Column(db.String(120), nullable=False, default='Bangalore, India')
    website = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    recruiter_name = db.Column(db.String(120), nullable=True)
    recruiter_email = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    jobs = db.relationship('Job', backref='company', cascade='all, delete-orphan')
    interviews = db.relationship('Interview', backref='company', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Company {self.name}>'


class Job(db.Model):
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    required_skills = db.Column(db.String(255), nullable=False)  # Comma-separated: "Python, SQL, JavaScript"
    min_cgpa = db.Column(db.Float, nullable=False, default=6.0)
    eligible_departments = db.Column(db.String(255), nullable=False, default='Computer Science, Information Technology, Electronics')
    graduation_year = db.Column(db.Integer, nullable=False, default=2026)
    salary_package = db.Column(db.String(50), nullable=False, default='6-8 LPA')
    salary_numeric = db.Column(db.Float, nullable=False, default=6.0)  # Numeric representation in LPA for charts/filtering
    location = db.Column(db.String(120), nullable=False, default='Bangalore')
    deadline = db.Column(db.String(50), nullable=False)  # e.g., '2026-10-15'
    openings = db.Column(db.Integer, nullable=False, default=5)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    applications = db.relationship('Application', backref='job', cascade='all, delete-orphan')
    interviews = db.relationship('Interview', backref='job', cascade='all, delete-orphan')

    def get_required_skills_list(self):
        if not self.required_skills:
            return []
        return [s.strip() for s in self.required_skills.split(',') if s.strip()]

    def get_eligible_departments_list(self):
        if not self.eligible_departments:
            return []
        return [d.strip() for d in self.eligible_departments.split(',') if d.strip()]

    def __repr__(self):
        return f'<Job {self.title}>'


class Application(db.Model):
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False)
    
    # Statuses: 'Applied', 'Under Review', 'Shortlisted', 'Interview Scheduled', 'Selected', 'Rejected'
    status = db.Column(db.String(50), nullable=False, default='Applied')
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    remarks = db.Column(db.String(255), nullable=True)
    
    # Relationships
    interviews = db.relationship('Interview', backref='application', cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('student_id', 'job_id', name='uq_student_job_application'),
    )

    def __repr__(self):
        return f'<Application Student {self.student_id} -> Job {self.job_id} ({self.status})>'


class Interview(db.Model):
    __tablename__ = 'interviews'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False)
    
    interview_date = db.Column(db.String(50), nullable=False)  # YYYY-MM-DD
    interview_time = db.Column(db.String(50), nullable=False)  # HH:MM
    mode = db.Column(db.String(50), nullable=False, default='Online (Google Meet)')  # 'Online', 'Offline'
    meeting_link = db.Column(db.String(255), nullable=True)
    round_name = db.Column(db.String(100), nullable=False, default='Technical Round 1')
    status = db.Column(db.String(50), default='Scheduled')  # 'Scheduled', 'Completed', 'Cancelled'
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Interview {self.round_name} for Student {self.student_id}>'


class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(255), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Notification {self.title} for User {self.user_id}>'
