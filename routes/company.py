from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from models import db, User, Company, Job, Application, Interview, StudentProfile, Notification
from routes.auth import role_required
from ai_engine.recommender import recommender

company_bp = Blueprint('company', __name__, url_prefix='/company')

def get_current_company():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return Company.query.filter_by(user_id=user_id).first()

@company_bp.route('/dashboard')
@role_required('company')
def dashboard():
    company = get_current_company()
    if not company:
        # Create default company linked to user if needed
        company = Company(
            user_id=session['user_id'],
            name=session.get('username', 'Company Partner'),
            industry='Information Technology'
        )
        db.session.add(company)
        db.session.commit()

    jobs = Job.query.filter_by(company_id=company.id).order_by(Job.created_at.desc()).all()
    job_ids = [j.id for j in jobs]

    applications = Application.query.filter(Application.job_id.in_(job_ids)).all() if job_ids else []
    
    total_applicants = len(applications)
    shortlisted = len([a for a in applications if a.status == 'Shortlisted'])
    interviews = Interview.query.filter_by(company_id=company.id).all()
    selected = len([a for a in applications if a.status == 'Selected'])

    return render_template('company/dashboard.html',
                           company=company,
                           jobs=jobs,
                           total_applicants=total_applicants,
                           shortlisted=shortlisted,
                           interviews_count=len(interviews),
                           selected=selected,
                           recent_applications=applications[:5])


@company_bp.route('/jobs/new', methods=['GET', 'POST'])
@role_required('company')
def post_job():
    company = get_current_company()
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        required_skills = request.form.get('required_skills', '').strip()
        min_cgpa = float(request.form.get('min_cgpa', 6.0) or 6.0)
        eligible_depts = request.form.get('eligible_departments', 'Computer Science, Information Technology').strip()
        grad_year = int(request.form.get('graduation_year', 2026) or 2026)
        salary_package = request.form.get('salary_package', '8 LPA').strip()
        salary_numeric = float(request.form.get('salary_numeric', 8.0) or 8.0)
        location = request.form.get('location', 'Bangalore').strip()
        deadline = request.form.get('deadline', '2026-11-30').strip()
        openings = int(request.form.get('openings', 5) or 5)

        if not title or not required_skills:
            flash('Please provide job title and required skills.', 'danger')
            return render_template('company/post_job.html', company=company)

        new_job = Job(
            company_id=company.id,
            title=title,
            description=description,
            required_skills=required_skills,
            min_cgpa=min_cgpa,
            eligible_departments=eligible_depts,
            graduation_year=grad_year,
            salary_package=salary_package,
            salary_numeric=salary_numeric,
            location=location,
            deadline=deadline,
            openings=openings,
            is_active=True
        )
        db.session.add(new_job)
        db.session.commit()

        # Notify eligible students about new job
        students = StudentProfile.query.all()
        for s in students:
            match_data = recommender.calculate_match(s, new_job)
            if match_data['is_eligible'] and match_data['match_score'] >= 65:
                notif = Notification(
                    user_id=s.user_id,
                    title="New Job Opportunity Match!",
                    message=f"{company.name} posted {new_job.title} which matches your profile ({match_data['match_score']}% Match)!",
                    link=url_for('student.job_detail', job_id=new_job.id)
                )
                db.session.add(notif)
        db.session.commit()

        flash('Job opportunity posted successfully! Eligible students have been notified.', 'success')
        return redirect(url_for('company.dashboard'))

    return render_template('company/post_job.html', company=company)


@company_bp.route('/jobs/<int:job_id>/edit', methods=['GET', 'POST'])
@role_required('company')
def edit_job(job_id):
    company = get_current_company()
    job = Job.query.filter_by(id=job_id, company_id=company.id).first_or_404()

    if request.method == 'POST':
        job.title = request.form.get('title', job.title).strip()
        job.description = request.form.get('description', job.description).strip()
        job.required_skills = request.form.get('required_skills', job.required_skills).strip()
        job.min_cgpa = float(request.form.get('min_cgpa', job.min_cgpa) or 6.0)
        job.eligible_departments = request.form.get('eligible_departments', job.eligible_departments).strip()
        job.graduation_year = int(request.form.get('graduation_year', job.graduation_year) or 2026)
        job.salary_package = request.form.get('salary_package', job.salary_package).strip()
        job.salary_numeric = float(request.form.get('salary_numeric', job.salary_numeric) or 8.0)
        job.location = request.form.get('location', job.location).strip()
        job.deadline = request.form.get('deadline', job.deadline).strip()
        job.openings = int(request.form.get('openings', job.openings) or 5)
        job.is_active = (request.form.get('is_active') == 'on')

        db.session.commit()
        flash('Job details updated successfully.', 'success')
        return redirect(url_for('company.dashboard'))

    return render_template('company/edit_job.html', job=job, company=company)


@company_bp.route('/applicants')
@role_required('company')
def applicants():
    company = get_current_company()
    job_id = request.args.get('job_id', type=int)

    company_jobs = Job.query.filter_by(company_id=company.id).all()
    job_ids = [j.id for j in company_jobs]

    query = Application.query.filter(Application.job_id.in_(job_ids))
    if job_id:
        query = query.filter(Application.job_id == job_id)

    applications = query.order_by(Application.applied_at.desc()).all()

    # Calculate AI Match score for each applicant
    applicant_cards = []
    for app in applications:
        match_data = recommender.calculate_match(app.student, app.job)
        applicant_cards.append({
            'application': app,
            'match_score': match_data['match_score'],
            'reasons': match_data['reasons'],
            'matched_skills': match_data['matched_skills'],
            'unmatched_skills': match_data['unmatched_skills']
        })

    # Sort applicants by AI match score descending
    applicant_cards.sort(key=lambda x: x['match_score'], reverse=True)

    return render_template('company/applicants.html',
                           applicants=applicant_cards,
                           jobs=company_jobs,
                           selected_job=job_id)


@company_bp.route('/applicants/<int:app_id>/status', methods=['POST'])
@role_required('company')
def update_candidate_status(app_id):
    company = get_current_company()
    app = Application.query.get_or_404(app_id)

    # Verify company owns this job
    if app.job.company_id != company.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('company.dashboard'))

    new_status = request.form.get('status', app.status)
    remarks = request.form.get('remarks', '').strip()

    app.status = new_status
    if remarks:
        app.remarks = remarks

    if new_status == 'Selected':
        app.student.placement_status = 'Placed'
        app.student.placed_company = company.name
        app.student.placed_package = app.job.salary_numeric

    # Notify student
    notif = Notification(
        user_id=app.student.user_id,
        title=f"Application Update: {company.name}",
        message=f"Your application status for {app.job.title} has changed to: {new_status}.",
        link=url_for('student.applications')
    )
    db.session.add(notif)
    db.session.commit()

    flash(f'Candidate status updated to {new_status}.', 'success')
    return redirect(request.referrer or url_for('company.applicants'))


@company_bp.route('/applicants/<int:app_id>/schedule-interview', methods=['POST'])
@role_required('company')
def schedule_interview(app_id):
    company = get_current_company()
    app = Application.query.get_or_404(app_id)

    if app.job.company_id != company.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('company.dashboard'))

    interview_date = request.form.get('interview_date')
    interview_time = request.form.get('interview_time')
    mode = request.form.get('mode', 'Online (Google Meet)')
    meeting_link = request.form.get('meeting_link', '')
    round_name = request.form.get('round_name', 'Technical Round 1')
    notes = request.form.get('notes', '')

    interview = Interview(
        application_id=app.id,
        student_id=app.student_id,
        company_id=company.id,
        job_id=app.job_id,
        interview_date=interview_date,
        interview_time=interview_time,
        mode=mode,
        meeting_link=meeting_link,
        round_name=round_name,
        notes=notes,
        status='Scheduled'
    )
    app.status = 'Interview Scheduled'
    db.session.add(interview)

    # Notify student
    notif = Notification(
        user_id=app.student.user_id,
        title=f"Interview Scheduled: {company.name}",
        message=f"Your {round_name} for {app.job.title} is scheduled for {interview_date} at {interview_time}.",
        link=url_for('student.interviews')
    )
    db.session.add(notif)
    db.session.commit()

    flash(f'Interview successfully scheduled with {app.student.full_name}!', 'success')
    return redirect(request.referrer or url_for('company.applicants'))


@company_bp.route('/profile', methods=['GET', 'POST'])
@role_required('company')
def profile():
    company = get_current_company()
    if request.method == 'POST':
        company.name = request.form.get('name', company.name).strip()
        company.industry = request.form.get('industry', company.industry).strip()
        company.location = request.form.get('location', company.location).strip()
        company.website = request.form.get('website', company.website).strip()
        company.description = request.form.get('description', company.description).strip()
        company.recruiter_name = request.form.get('recruiter_name', company.recruiter_name).strip()
        company.recruiter_email = request.form.get('recruiter_email', company.recruiter_email).strip()
        if request.form.get('logo_url'):
            company.logo_url = request.form.get('logo_url').strip()

        db.session.commit()
        session['display_name'] = company.name
        flash('Company profile updated successfully.', 'success')
        return redirect(url_for('company.profile'))

    return render_template('company/profile.html', company=company)
