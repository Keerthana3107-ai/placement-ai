import os
from flask import Flask, render_template, redirect, url_for, session, send_from_directory
from config import Config
from models import db, User, StudentProfile, Company, Job, Notification

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['ML_MODEL_PATH'], exist_ok=True)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.student import student_bp
    from routes.admin import admin_bp
    from routes.company import company_bp
    from routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(api_bp)

    # Context processors for global template variables
    @app.context_processor
    def inject_globals():
        user = None
        unread_notif_count = 0
        recent_notifs = []

        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            if user:
                unread_notif_count = Notification.query.filter_by(user_id=user.id, is_read=False).count()
                recent_notifs = Notification.query.filter_by(user_id=user.id).order_by(Notification.created_at.desc()).limit(5).all()

        return {
            'current_user': user,
            'user_role': session.get('user_role'),
            'unread_notif_count': unread_notif_count,
            'recent_notifs': recent_notifs
        }

    # Custom Jinja Template Filters
    @app.template_filter('status_badge')
    def status_badge_filter(status):
        badges = {
            'Applied': 'bg-secondary',
            'Under Review': 'bg-info text-dark',
            'Shortlisted': 'bg-primary',
            'Interview Scheduled': 'bg-warning text-dark',
            'Selected': 'bg-success',
            'Rejected': 'bg-danger',
            'Scheduled': 'bg-info text-dark',
            'Completed': 'bg-success',
            'Cancelled': 'bg-secondary',
            'Placed': 'bg-success',
            'Unplaced': 'bg-secondary',
            'Opted Out': 'bg-warning text-dark'
        }
        return badges.get(status, 'bg-light text-dark')

    # Root route: landing page or dashboard redirect
    @app.route('/')
    def index():
        if 'user_id' in session:
            role = session.get('user_role')
            if role == 'student':
                return redirect(url_for('student.dashboard'))
            elif role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif role == 'company':
                return redirect(url_for('company.dashboard'))
        
        # Public statistics for landing page
        stats = {
            'total_students': StudentProfile.query.count(),
            'total_companies': Company.query.count(),
            'active_jobs': Job.query.filter_by(is_active=True).count(),
            'featured_companies': Company.query.limit(6).all(),
            'featured_jobs': Job.query.filter_by(is_active=True).limit(6).all()
        }
        return render_template('index.html', **stats)

    # Route to serve uploaded resumes safely
    @app.route('/uploads/resumes/<filename>')
    def uploaded_resume(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    # Auto create database tables
    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
