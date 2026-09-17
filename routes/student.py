import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app, jsonify
from werkzeug.utils import secure_filename
from models import db, User, StudentProfile, Skill, Project, Certification, Job, Application, Interview, Notification
from routes.auth import login_required, role_required
from ai_engine.recommender import recommender
from ai_engine.resume_parser import resume_parser

student_bp = Blueprint('student', __name__, url_prefix='/student')

def get_current_student():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return StudentProfile.query.filter_by(user_id=user_id).first()

@student_bp.route('/dashboard')
@role_required('student')
def dashboard():
    student = get_current_student()
    if not student:
        flash('Please complete your profile to continue.', 'info')
        return redirect(url_for('student.profile'))

    # Calculate Profile Completion
    completion_pct, breakdown, suggestions = student.calculate_profile_completion()

    # Application Statistics
    total_apps = len(student.applications)
    shortlisted_apps = len([a for a in student.applications if a.status in ['Shortlisted', 'Interview Scheduled', 'Selected']])
    selected_apps = len([a for a in student.applications if a.status == 'Selected'])
    
    # Upcoming Interviews
    interviews = Interview.query.filter_by(student_id=student.id).order_by(Interview.interview_date.asc(), Interview.interview_time.asc()).all()
    upcoming_interviews = [i for i in interviews if i.status == 'Scheduled']
    next_interview = upcoming_interviews[0] if upcoming_interviews else None

    # Application Status Breakdown for Chart
    status_counts = {
        'Applied': 0,
        'Under Review': 0,
        'Shortlisted': 0,
        'Interview Scheduled': 0,
        'Selected': 0,
        'Rejected': 0
    }
    for app in student.applications:
        if app.status in status_counts:
            status_counts[app.status] += 1
        else:
            status_counts['Applied'] += 1

    # AI-Recommended Jobs (Top 4)
    active_jobs = Job.query.filter_by(is_active=True).all()
    applied_job_ids = [a.job_id for a in student.applications]
    available_jobs = [j for j in active_jobs if j.id not in applied_job_ids]
    
    recommendations = recommender.get_recommendations(student, available_jobs, top_n=4)

    return render_template('student/dashboard.html',
                           student=student,
                           completion_pct=completion_pct,
                           breakdown=breakdown,
                           suggestions=suggestions,
                           total_apps=total_apps,
                           shortlisted_apps=shortlisted_apps,
                           selected_apps=selected_apps,
                           interviews=upcoming_interviews,
                           next_interview=next_interview,
                           status_counts=status_counts,
                           recommendations=recommendations)


@student_bp.route('/profile', methods=['GET', 'POST'])
@role_required('student')
def profile():
    student = get_current_student()
    if not student:
        # Create empty profile if not exists
        student = StudentProfile(user_id=session['user_id'], full_name=session.get('username', 'Student'))
        db.session.add(student)
        db.session.commit()

    if request.method == 'POST':
        action = request.form.get('action')
        
        # 1. Update Personal & Academic Information
        if action == 'update_info':
            student.full_name = request.form.get('full_name', student.full_name).strip()
            student.phone = request.form.get('phone', '').strip()
            student.department = request.form.get('department', student.department).strip()
            student.college = request.form.get('college', student.college).strip()
            
            try:
                student.graduation_year = int(request.form.get('graduation_year', student.graduation_year) or 2026)
                student.cgpa = float(request.form.get('cgpa', student.cgpa) or 0.0)
                student.tenth_pct = float(request.form.get('tenth_pct', 0.0) or 0.0) if request.form.get('tenth_pct') else None
                student.twelfth_pct = float(request.form.get('twelfth_pct', 0.0) or 0.0) if request.form.get('twelfth_pct') else None
            except ValueError:
                flash('Please enter valid numeric values for CGPA and percentages.', 'danger')
                return redirect(url_for('student.profile'))

            db.session.commit()
            session['display_name'] = student.full_name
            flash('Profile details updated successfully!', 'success')
            return redirect(url_for('student.profile'))

        # 2. Add Skill
        elif action == 'add_skill':
            skill_name = request.form.get('skill_name', '').strip()
            proficiency = request.form.get('proficiency', 'Intermediate').strip()
            if skill_name:
                # Check for existing skill
                existing = Skill.query.filter_by(student_id=student.id, skill_name=skill_name).first()
                if not existing:
                    new_skill = Skill(student_id=student.id, skill_name=skill_name, proficiency=proficiency)
                    db.session.add(new_skill)
                    db.session.commit()
                    flash(f'Skill "{skill_name}" added.', 'success')
                else:
                    flash(f'Skill "{skill_name}" is already in your profile.', 'info')
            return redirect(url_for('student.profile', tab='skills'))

        # 3. Add Project
        elif action == 'add_project':
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            tech_stack = request.form.get('tech_stack', '').strip()
            if title and description:
                new_project = Project(student_id=student.id, title=title, description=description, tech_stack=tech_stack)
                db.session.add(new_project)
                db.session.commit()
                flash('Project added successfully!', 'success')
            else:
                flash('Please enter both title and description for the project.', 'danger')
            return redirect(url_for('student.profile', tab='projects'))

        # 4. Add Certification
        elif action == 'add_certification':
            title = request.form.get('title', '').strip()
            issuer = request.form.get('issuer', '').strip()
            year = request.form.get('issue_year')
            issue_year = int(year) if year and year.isdigit() else None
            if title and issuer:
                cert = Certification(student_id=student.id, title=title, issuer=issuer, issue_year=issue_year)
                db.session.add(cert)
                db.session.commit()
                flash('Certification added successfully!', 'success')
            else:
                flash('Please enter certification title and issuing organization.', 'danger')
            return redirect(url_for('student.profile', tab='certifications'))

    completion_pct, breakdown, suggestions = student.calculate_profile_completion()
    return render_template('student/profile.html',
                           student=student,
                           completion_pct=completion_pct,
                           breakdown=breakdown,
                           suggestions=suggestions)


@student_bp.route('/profile/delete-skill/<int:skill_id>', methods=['POST'])
@role_required('student')
def delete_skill(skill_id):
    student = get_current_student()
    skill = Skill.query.filter_by(id=skill_id, student_id=student.id).first_or_404()
    db.session.delete(skill)
    db.session.commit()
    flash(f'Skill "{skill.skill_name}" removed.', 'info')
    return redirect(url_for('student.profile', tab='skills'))


@student_bp.route('/profile/delete-project/<int:project_id>', methods=['POST'])
@role_required('student')
def delete_project(project_id):
    student = get_current_student()
    proj = Project.query.filter_by(id=project_id, student_id=student.id).first_or_404()
    db.session.delete(proj)
    db.session.commit()
    flash('Project deleted.', 'info')
    return redirect(url_for('student.profile', tab='projects'))


@student_bp.route('/profile/delete-certification/<int:cert_id>', methods=['POST'])
@role_required('student')
def delete_certification(cert_id):
    student = get_current_student()
    cert = Certification.query.filter_by(id=cert_id, student_id=student.id).first_or_404()
    db.session.delete(cert)
    db.session.commit()
    flash('Certification deleted.', 'info')
    return redirect(url_for('student.profile', tab='certifications'))


@student_bp.route('/resume/upload', methods=['POST'])
@role_required('student')
def upload_resume():
    student = get_current_student()
    if 'resume_file' not in request.files:
        flash('No file selected.', 'danger')
        return redirect(url_for('student.profile', tab='resume'))

    file = request.files['resume_file']
    if file.filename == '':
        flash('No file selected.', 'danger')
        return redirect(url_for('student.profile', tab='resume'))

    if file and file.filename.lower().endswith('.pdf'):
        filename = secure_filename(f"student_{student.id}_{file.filename}")
        upload_dir = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)

        student.resume_filename = filename

        # AI Resume Skill Analysis
        analysis_result = resume_parser.analyze_resume(file_path)
        extracted_skills = []
        if analysis_result['success']:
            extracted_skills = analysis_result['skills']
            student.resume_extracted_text = analysis_result['text']

            # Check if auto-import was requested
            auto_import = request.form.get('auto_import_skills') == 'on'
            if auto_import and extracted_skills:
                existing_skill_names = [s.lower() for s in student.get_skill_names()]
                added_count = 0
                for skill_name in extracted_skills:
                    if skill_name.lower() not in existing_skill_names:
                        db.session.add(Skill(student_id=student.id, skill_name=skill_name, proficiency='Intermediate'))
                        added_count += 1
                if added_count > 0:
                    flash(f'Resume analyzed! Automatically added {added_count} new detected skills to your profile.', 'success')

            flash('Resume uploaded and analyzed successfully!', 'success')
        else:
            flash(f'Resume uploaded, but skill extraction note: {analysis_result.get("error")}', 'warning')

        db.session.commit()
        return redirect(url_for('student.profile', tab='resume', skills_detected=",".join(extracted_skills)))
    else:
        flash('Only PDF resumes are supported.', 'danger')
        return redirect(url_for('student.profile', tab='resume'))


@student_bp.route('/jobs')
@role_required('student')
def jobs():
    student = get_current_student()
    search_query = request.args.get('q', '').strip().lower()
    selected_dept = request.args.get('department', '').strip()
    selected_location = request.args.get('location', '').strip()
    min_package = request.args.get('min_package', type=float)
    eligible_only = request.args.get('eligible_only') == '1'

    query = Job.query.filter_by(is_active=True)

    if selected_location:
        query = query.filter(Job.location.ilike(f'%{selected_location}%'))

    if min_package:
        query = query.filter(Job.salary_numeric >= min_package)

    all_jobs = query.order_by(Job.created_at.desc()).all()

    # Filter by text search if provided
    if search_query:
        all_jobs = [
            j for j in all_jobs if
            search_query in j.title.lower() or
            search_query in (j.company.name if j.company else '').lower() or
            search_query in j.required_skills.lower() or
            search_query in j.location.lower()
        ]

    # Compute eligibility & match score for all jobs
    jobs_with_meta = []
    applied_job_ids = {a.job_id: a for a in student.applications}

    for job in all_jobs:
        match_info = recommender.calculate_match(student, job)
        if eligible_only and not match_info['is_eligible']:
            continue

        jobs_with_meta.append({
            'job': job,
            'match_score': match_info['match_score'],
            'is_eligible': match_info['is_eligible'],
            'reasons': match_info['reasons'],
            'missing_reasons': match_info['missing_reasons'],
            'matched_skills': match_info['matched_skills'],
            'unmatched_skills': match_info['unmatched_skills'],
            'application': applied_job_ids.get(job.id)
        })

    # Sort: Eligible first, then by match score descending
    jobs_with_meta.sort(key=lambda x: (1 if x['is_eligible'] else 0, x['match_score']), reverse=True)

    # Distinct locations for filter dropdown
    locations = sorted(list(set([j.location for j in Job.query.filter_by(is_active=True).all() if j.location])))

    return render_template('student/jobs.html',
                           student=student,
                           jobs=jobs_with_meta,
                           search_query=search_query,
                           selected_location=selected_location,
                           min_package=min_package,
                           eligible_only=eligible_only,
                           locations=locations)


@student_bp.route('/jobs/<int:job_id>')
@role_required('student')
def job_detail(job_id):
    student = get_current_student()
    job = Job.query.get_or_404(job_id)
    
    # Calculate eligibility and explainable match breakdown
    match_data = recommender.calculate_match(student, job)
    existing_application = Application.query.filter_by(student_id=student.id, job_id=job.id).first()

    return render_template('student/job_detail.html',
                           student=student,
                           job=job,
                           match_data=match_data,
                           application=existing_application)


@student_bp.route('/jobs/<int:job_id>/apply', methods=['POST'])
@role_required('student')
def apply_job(job_id):
    student = get_current_student()
    job = Job.query.get_or_404(job_id)

    # Check if already applied
    existing = Application.query.filter_by(student_id=student.id, job_id=job.id).first()
    if existing:
        flash('You have already applied for this position.', 'info')
        return redirect(url_for('student.job_detail', job_id=job.id))

    # Enforce strict Eligibility Check
    is_eligible, passed_reasons, failure_reasons = recommender.check_eligibility(student, job)
    if not is_eligible:
        reason_str = " | ".join(failure_reasons)
        flash(f'Application rejected: You do not meet the eligibility requirements. {reason_str}', 'danger')
        return redirect(url_for('student.job_detail', job_id=job.id))

    # Create application
    application = Application(
        student_id=student.id,
        job_id=job.id,
        status='Applied',
        remarks='Application submitted through Placement Portal.'
    )
    db.session.add(application)

    # Notify student
    notif = Notification(
        user_id=session['user_id'],
        title="Application Submitted",
        message=f"You successfully applied for {job.title} at {job.company.name}.",
        link=url_for('student.applications')
    )
    db.session.add(notif)
    db.session.commit()

    flash(f'Congratulations! Your application for {job.title} at {job.company.name} was successfully submitted.', 'success')
    return redirect(url_for('student.applications'))


@student_bp.route('/applications')
@role_required('student')
def applications():
    student = get_current_student()
    user_apps = Application.query.filter_by(student_id=student.id).order_by(Application.applied_at.desc()).all()
    return render_template('student/applications.html', student=student, applications=user_apps)


@student_bp.route('/interviews')
@role_required('student')
def interviews():
    student = get_current_student()
    interviews_list = Interview.query.filter_by(student_id=student.id).order_by(Interview.interview_date.asc(), Interview.interview_time.asc()).all()
    return render_template('student/interviews.html', student=student, interviews=interviews_list)


@student_bp.route('/recommendations')
@role_required('student')
def recommendations():
    student = get_current_student()
    active_jobs = Job.query.filter_by(is_active=True).all()
    applied_job_ids = [a.job_id for a in student.applications]
    available_jobs = [j for j in active_jobs if j.id not in applied_job_ids]

    recommended_list = recommender.get_recommendations(student, available_jobs, top_n=20)
    return render_template('student/recommendations.html', student=student, recommendations=recommended_list)
