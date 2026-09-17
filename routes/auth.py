from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from models import db, User, StudentProfile, Company

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in first.', 'warning')
                return redirect(url_for('auth.login'))
            user_role = session.get('user_role')
            if user_role not in roles:
                flash(f'Unauthorized access. You need a {", ".join(roles)} account to access this page.', 'danger')
                if user_role == 'student':
                    return redirect(url_for('student.dashboard'))
                elif user_role == 'admin':
                    return redirect(url_for('admin.dashboard'))
                elif user_role == 'company':
                    return redirect(url_for('company.dashboard'))
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        role = session.get('user_role')
        if role == 'student':
            return redirect(url_for('student.dashboard'))
        elif role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif role == 'company':
            return redirect(url_for('company.dashboard'))

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '').strip()
        
        user = User.query.filter((User.email == identifier) | (User.username == identifier)).first()
        
        if user and user.check_password(password):
            session.clear()
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_role'] = user.role
            session['email'] = user.email

            # Store display name
            if user.role == 'student' and user.student_profile:
                session['display_name'] = user.student_profile.full_name
            elif user.role == 'company' and user.company_profile:
                session['display_name'] = user.company_profile.name
            else:
                session['display_name'] = user.username

            flash(f'Welcome back, {session["display_name"]}!', 'success')
            
            next_url = request.args.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)

            if user.role == 'student':
                return redirect(url_for('student.dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'company':
                return redirect(url_for('company.dashboard'))
        else:
            flash('Invalid username/email or password. Please try again.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        role = request.form.get('role', 'student').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        # Validation
        if not username or not email or not password:
            flash('Please fill in all required fields.', 'danger')
            return render_template('auth/register.html', role=role)

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html', role=role)

        if User.query.filter_by(username=username).first():
            flash('Username is already taken. Please choose another.', 'danger')
            return render_template('auth/register.html', role=role)

        if User.query.filter_by(email=email).first():
            flash('Email is already registered. Please login.', 'danger')
            return render_template('auth/register.html', role=role)

        # Create user
        new_user = User(username=username, email=email, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()

        # Create profile based on role
        if role == 'student':
            full_name = request.form.get('full_name', username).strip()
            department = request.form.get('department', 'Computer Science').strip()
            cgpa = float(request.form.get('cgpa', 7.5) or 7.5)
            grad_year = int(request.form.get('graduation_year', 2026) or 2026)
            phone = request.form.get('phone', '').strip()

            profile = StudentProfile(
                user_id=new_user.id,
                full_name=full_name,
                department=department,
                cgpa=cgpa,
                graduation_year=grad_year,
                phone=phone
            )
            db.session.add(profile)

        elif role == 'company':
            company_name = request.form.get('company_name', username).strip()
            industry = request.form.get('industry', 'Information Technology').strip()
            location = request.form.get('location', 'Bangalore').strip()
            website = request.form.get('website', '').strip()

            company = Company(
                user_id=new_user.id,
                name=company_name,
                industry=industry,
                location=location,
                website=website,
                recruiter_name=request.form.get('recruiter_name', username),
                recruiter_email=email
            )
            db.session.add(company)

        db.session.commit()
        flash('Account registered successfully! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
