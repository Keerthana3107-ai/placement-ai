from flask import Blueprint, jsonify, request, session
from models import db, User, StudentProfile, Company, Job, Application, Interview, Notification
from ai_engine.recommender import recommender
from collections import Counter
from datetime import datetime, timedelta

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/check-eligibility/<int:job_id>')
def check_eligibility(job_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    student = StudentProfile.query.filter_by(user_id=user_id).first()
    job = Job.query.get(job_id)

    if not student or not job:
        return jsonify({'error': 'Student or Job not found'}), 404

    is_eligible, passed_reasons, failure_reasons = recommender.check_eligibility(student, job)
    
    return jsonify({
        'job_id': job.id,
        'job_title': job.title,
        'company_name': job.company.name,
        'is_eligible': is_eligible,
        'student_cgpa': student.cgpa,
        'required_cgpa': job.min_cgpa,
        'student_dept': student.department,
        'eligible_depts': job.eligible_departments,
        'passed_reasons': passed_reasons,
        'failure_reasons': failure_reasons
    })


@api_bp.route('/job-match-score/<int:job_id>')
def job_match_score(job_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    student = StudentProfile.query.filter_by(user_id=user_id).first()
    job = Job.query.get(job_id)

    if not student or not job:
        return jsonify({'error': 'Student or Job not found'}), 404

    match_data = recommender.calculate_match(student, job)
    return jsonify(match_data)


@api_bp.route('/notifications')
def get_notifications():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'unread_count': 0, 'notifications': []})

    notifs = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).limit(8).all()
    unread_count = Notification.query.filter_by(user_id=user_id, is_read=False).count()

    return jsonify({
        'unread_count': unread_count,
        'notifications': [{
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'link': n.link,
            'is_read': n.is_read,
            'created_at': n.created_at.strftime('%b %d, %H:%M')
        } for n in notifs]
    })


@api_bp.route('/notifications/<int:notif_id>/read', methods=['POST'])
def mark_notification_read(notif_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    notif = Notification.query.filter_by(id=notif_id, user_id=user_id).first()
    if notif:
        notif.is_read = True
        db.session.commit()
    return jsonify({'success': True})


@api_bp.route('/notifications/mark-all-read', methods=['POST'])
def mark_all_notifications_read():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify({'success': True})


@api_bp.route('/admin/chart-data')
def admin_chart_data():
    if session.get('user_role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    # 1. Applications by Company
    companies = Company.query.all()
    company_labels = []
    company_app_counts = []
    for c in companies:
        app_count = Application.query.join(Job).filter(Job.company_id == c.id).count()
        if app_count > 0:
            company_labels.append(c.name)
            company_app_counts.append(app_count)

    # 2. Placement Status (Placed vs Unplaced)
    placed_count = StudentProfile.query.filter_by(placement_status='Placed').count()
    unplaced_count = StudentProfile.query.filter_by(placement_status='Unplaced').count()
    opted_out = StudentProfile.query.filter_by(placement_status='Opted Out').count()

    # 3. Department-wise Placements
    all_students = StudentProfile.query.all()
    dept_map = {}
    for s in all_students:
        dept = s.department or 'Other'
        if dept not in dept_map:
            dept_map[dept] = {'total': 0, 'placed': 0}
        dept_map[dept]['total'] += 1
        if s.placement_status == 'Placed':
            dept_map[dept]['placed'] += 1

    dept_labels = list(dept_map.keys())
    dept_placed = [dept_map[d]['placed'] for d in dept_labels]
    dept_unplaced = [dept_map[d]['total'] - dept_map[d]['placed'] for d in dept_labels]

    # 4. Monthly Application Trends
    # Group applications by month
    apps = Application.query.all()
    trend_map = {}
    for a in apps:
        month_label = a.applied_at.strftime('%b %Y') if a.applied_at else 'Recent'
        trend_map[month_label] = trend_map.get(month_label, 0) + 1

    if not trend_map:
        trend_map = {'Current Period': len(apps)}

    trend_labels = list(trend_map.keys())
    trend_counts = list(trend_map.values())

    # 5. Salary/Package Distribution
    jobs = Job.query.all()
    salary_buckets = {
        '< 5 LPA': 0,
        '5 - 8 LPA': 0,
        '8 - 12 LPA': 0,
        '12 - 20 LPA': 0,
        '> 20 LPA': 0
    }
    for j in jobs:
        pkg = j.salary_numeric or 6.0
        if pkg < 5.0:
            salary_buckets['< 5 LPA'] += 1
        elif pkg <= 8.0:
            salary_buckets['5 - 8 LPA'] += 1
        elif pkg <= 12.0:
            salary_buckets['8 - 12 LPA'] += 1
        elif pkg <= 20.0:
            salary_buckets['12 - 20 LPA'] += 1
        else:
            salary_buckets['> 20 LPA'] += 1

    return jsonify({
        'applications_by_company': {
            'labels': company_labels,
            'data': company_app_counts
        },
        'placement_status': {
            'labels': ['Placed', 'Unplaced', 'Opted Out'],
            'data': [placed_count, unplaced_count, opted_out]
        },
        'dept_placements': {
            'labels': dept_labels,
            'placed': dept_placed,
            'unplaced': dept_unplaced
        },
        'application_trends': {
            'labels': trend_labels,
            'data': trend_counts
        },
        'salary_distribution': {
            'labels': list(salary_buckets.keys()),
            'data': list(salary_buckets.values())
        }
    })


@api_bp.route('/student/chart-data')
def student_chart_data():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    student = StudentProfile.query.filter_by(user_id=user_id).first()
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    # Application status counts
    status_counts = Counter([a.status for a in student.applications])
    statuses = ['Applied', 'Under Review', 'Shortlisted', 'Interview Scheduled', 'Selected', 'Rejected']
    data = [status_counts.get(s, 0) for s in statuses]

    # Student skills
    skills = [s.skill_name for s in student.skills]

    return jsonify({
        'statuses': {
            'labels': statuses,
            'data': data
        },
        'skills': skills
    })
