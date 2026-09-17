import io
import csv
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, Response, jsonify
from models import db, User, StudentProfile, Company, Job, Application, Interview, Notification
from routes.auth import role_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@role_required('admin')
def dashboard():
    # Overall Key Metrics
    total_students = StudentProfile.query.count()
    total_companies = Company.query.count()
    active_jobs = Job.query.filter_by(is_active=True).count()
    total_applications = Application.query.count()
    
    placed_students = StudentProfile.query.filter(StudentProfile.placement_status == 'Placed').count()
    placement_pct = round((placed_students / total_students * 100), 1) if total_students > 0 else 0

    # Recent activities
    recent_applications = Application.query.order_by(Application.applied_at.desc()).limit(6).all()
    upcoming_interviews = Interview.query.filter_by(status='Scheduled').order_by(Interview.interview_date.asc(), Interview.interview_time.asc()).limit(5).all()

    return render_template('admin/dashboard.html',
                           total_students=total_students,
                           total_companies=total_companies,
                           active_jobs=active_jobs,
                           total_applications=total_applications,
                           placed_students=placed_students,
                           placement_pct=placement_pct,
                           recent_applications=recent_applications,
                           upcoming_interviews=upcoming_interviews)


@admin_bp.route('/companies', methods=['GET', 'POST'])
@role_required('admin')
def companies():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'create':
            name = request.form.get('name', '').strip()
            industry = request.form.get('industry', 'IT').strip()
            location = request.form.get('location', 'Bangalore').strip()
            website = request.form.get('website', '').strip()
            description = request.form.get('description', '').strip()
            recruiter_name = request.form.get('recruiter_name', '').strip()
            recruiter_email = request.form.get('recruiter_email', '').strip()
            logo_url = request.form.get('logo_url', '').strip()

            if not name:
                flash('Company name is required.', 'danger')
                return redirect(url_for('admin.companies'))

            company = Company(
                name=name,
                industry=industry,
                location=location,
                website=website,
                description=description,
                recruiter_name=recruiter_name,
                recruiter_email=recruiter_email,
                logo_url=logo_url or f"https://ui-avatars.com/api/?name={name.replace(' ', '+')}&background=0D8ABC&color=fff"
            )
            db.session.add(company)
            db.session.commit()
            flash(f'Company "{name}" created successfully.', 'success')

        elif action == 'edit':
            company_id = request.form.get('company_id')
            company = Company.query.get_or_404(company_id)
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
            flash(f'Company "{company.name}" updated successfully.', 'success')

        return redirect(url_for('admin.companies'))

    all_companies = Company.query.order_by(Company.name.asc()).all()
    return render_template('admin/companies.html', companies=all_companies)


@admin_bp.route('/companies/delete/<int:company_id>', methods=['POST'])
@role_required('admin')
def delete_company(company_id):
    company = Company.query.get_or_404(company_id)
    name = company.name
    db.session.delete(company)
    db.session.commit()
    flash(f'Company "{name}" deleted successfully.', 'info')
    return redirect(url_for('admin.companies'))


@admin_bp.route('/jobs', methods=['GET', 'POST'])
@role_required('admin')
def jobs():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'create':
            company_id = request.form.get('company_id')
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            required_skills = request.form.get('required_skills', '').strip()
            min_cgpa = float(request.form.get('min_cgpa', 6.0) or 6.0)
            eligible_depts = request.form.get('eligible_departments', 'Computer Science, Information Technology').strip()
            grad_year = int(request.form.get('graduation_year', 2026) or 2026)
            salary_package = request.form.get('salary_package', '6-8 LPA').strip()
            salary_numeric = float(request.form.get('salary_numeric', 7.0) or 7.0)
            location = request.form.get('location', 'Bangalore').strip()
            deadline = request.form.get('deadline', '2026-11-30').strip()
            openings = int(request.form.get('openings', 5) or 5)

            new_job = Job(
                company_id=company_id,
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
            flash(f'Job opportunity "{title}" posted successfully.', 'success')

        elif action == 'edit':
            job_id = request.form.get('job_id')
            job = Job.query.get_or_404(job_id)
            job.title = request.form.get('title', job.title).strip()
            job.company_id = request.form.get('company_id', job.company_id)
            job.description = request.form.get('description', job.description).strip()
            job.required_skills = request.form.get('required_skills', job.required_skills).strip()
            job.min_cgpa = float(request.form.get('min_cgpa', job.min_cgpa) or 6.0)
            job.eligible_departments = request.form.get('eligible_departments', job.eligible_departments).strip()
            job.graduation_year = int(request.form.get('graduation_year', job.graduation_year) or 2026)
            job.salary_package = request.form.get('salary_package', job.salary_package).strip()
            job.salary_numeric = float(request.form.get('salary_numeric', job.salary_numeric) or 7.0)
            job.location = request.form.get('location', job.location).strip()
            job.deadline = request.form.get('deadline', job.deadline).strip()
            job.openings = int(request.form.get('openings', job.openings) or 5)
            job.is_active = (request.form.get('is_active') == 'on')

            db.session.commit()
            flash(f'Job "{job.title}" updated successfully.', 'success')

        return redirect(url_for('admin.jobs'))

    all_jobs = Job.query.order_by(Job.created_at.desc()).all()
    all_companies = Company.query.order_by(Company.name.asc()).all()
    return render_template('admin/jobs.html', jobs=all_jobs, companies=all_companies)


@admin_bp.route('/jobs/delete/<int:job_id>', methods=['POST'])
@role_required('admin')
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    title = job.title
    db.session.delete(job)
    db.session.commit()
    flash(f'Job "{title}" deleted.', 'info')
    return redirect(url_for('admin.jobs'))


@admin_bp.route('/students')
@role_required('admin')
def students():
    department = request.args.get('department', '').strip()
    status = request.args.get('status', '').strip()
    search = request.args.get('search', '').strip().lower()

    query = StudentProfile.query

    if department:
        query = query.filter(StudentProfile.department == department)
    if status:
        query = query.filter(StudentProfile.placement_status == status)

    all_students = query.order_by(StudentProfile.cgpa.desc()).all()

    if search:
        all_students = [
            s for s in all_students if
            search in s.full_name.lower() or
            search in (s.user.email if s.user else '').lower() or
            search in (s.department or '').lower() or
            search in " ".join(s.get_skill_names()).lower()
        ]

    departments = sorted(list(set([s.department for s in StudentProfile.query.all() if s.department])))
    return render_template('admin/students.html', students=all_students, departments=departments, selected_dept=department, selected_status=status, search=search)


@admin_bp.route('/students/<int:student_id>/update-placement', methods=['POST'])
@role_required('admin')
def update_placement_status(student_id):
    student = StudentProfile.query.get_or_404(student_id)
    new_status = request.form.get('placement_status', 'Unplaced')
    placed_company = request.form.get('placed_company', '').strip()
    placed_pkg = request.form.get('placed_package')
    
    student.placement_status = new_status
    if new_status == 'Placed':
        student.placed_company = placed_company
        student.placed_package = float(placed_pkg) if placed_pkg else None
    else:
        student.placed_company = None
        student.placed_package = None

    db.session.commit()

    # Notify student
    notif = Notification(
        user_id=student.user_id,
        title="Placement Status Updated",
        message=f"Your placement status has been updated to '{new_status}'." + (f" Company: {placed_company}!" if placed_company else ""),
        link=url_for('student.dashboard')
    )
    db.session.add(notif)
    db.session.commit()

    flash(f"Updated placement status for {student.full_name}.", 'success')
    return redirect(url_for('admin.students'))


@admin_bp.route('/applications')
@role_required('admin')
def applications():
    status_filter = request.args.get('status', '').strip()
    job_id = request.args.get('job_id', type=int)

    query = Application.query

    if status_filter:
        query = query.filter(Application.status == status_filter)
    if job_id:
        query = query.filter(Application.job_id == job_id)

    all_apps = query.order_by(Application.applied_at.desc()).all()
    all_jobs = Job.query.all()

    return render_template('admin/applications.html',
                           applications=all_apps,
                           jobs=all_jobs,
                           selected_status=status_filter,
                           selected_job=job_id)


@admin_bp.route('/applications/<int:app_id>/update-status', methods=['POST'])
@role_required('admin')
def update_application_status(app_id):
    app = Application.query.get_or_404(app_id)
    new_status = request.form.get('status', app.status)
    remarks = request.form.get('remarks', '').strip()

    app.status = new_status
    if remarks:
        app.remarks = remarks

    # If selected, also automatically update student placement record
    if new_status == 'Selected':
        app.student.placement_status = 'Placed'
        app.student.placed_company = app.job.company.name
        app.student.placed_package = app.job.salary_numeric

    # Notify student
    notif = Notification(
        user_id=app.student.user_id,
        title=f"Application Status: {new_status}",
        message=f"Your application for {app.job.title} at {app.job.company.name} is now: {new_status}.",
        link=url_for('student.applications')
    )
    db.session.add(notif)
    db.session.commit()

    flash(f'Application #{app.id} status changed to {new_status}.', 'success')
    return redirect(request.referrer or url_for('admin.applications'))


@admin_bp.route('/interviews', methods=['GET', 'POST'])
@role_required('admin')
def interviews():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'schedule':
            application_id = request.form.get('application_id')
            app = Application.query.get_or_404(application_id)
            
            interview_date = request.form.get('interview_date')
            interview_time = request.form.get('interview_time')
            mode = request.form.get('mode', 'Online (Google Meet)')
            meeting_link = request.form.get('meeting_link', '')
            round_name = request.form.get('round_name', 'Technical Round 1')
            notes = request.form.get('notes', '')

            new_interview = Interview(
                application_id=app.id,
                student_id=app.student_id,
                company_id=app.job.company_id,
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
            db.session.add(new_interview)

            # Notify student
            notif = Notification(
                user_id=app.student.user_id,
                title=f"Interview Scheduled: {round_name}",
                message=f"You have an interview scheduled with {app.job.company.name} on {interview_date} at {interview_time}.",
                link=url_for('student.interviews')
            )
            db.session.add(notif)
            db.session.commit()

            flash('Interview successfully scheduled!', 'success')
            return redirect(url_for('admin.interviews'))

    all_interviews = Interview.query.order_by(Interview.interview_date.asc(), Interview.interview_time.asc()).all()
    shortlisted_apps = Application.query.filter(Application.status.in_(['Shortlisted', 'Applied', 'Under Review'])).all()

    return render_template('admin/interviews.html', interviews=all_interviews, applications=shortlisted_apps)


@admin_bp.route('/reports/export-csv')
@role_required('admin')
def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)

    # Headers
    writer.writerow(['Student ID', 'Full Name', 'Email', 'Phone', 'Department', 'CGPA', 'Graduation Year', 'Placement Status', 'Placed Company', 'Placed Package (LPA)'])

    students = StudentProfile.query.all()
    for s in students:
        writer.writerow([
            s.id,
            s.full_name,
            s.user.email if s.user else '',
            s.phone or '',
            s.department,
            s.cgpa,
            s.graduation_year,
            s.placement_status,
            s.placed_company or 'N/A',
            s.placed_package or 'N/A'
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=placement_report_{datetime.now().strftime('%Y%m%d')}.csv"}
    )
