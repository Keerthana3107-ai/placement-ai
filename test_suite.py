import unittest
from app import create_app
from models import db, User, StudentProfile, Job, Application, Interview
from ai_engine.recommender import recommender
from ai_engine.resume_parser import resume_parser

class PlacementPortalTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def test_01_landing_page(self):
        """Test public landing page"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'AI-Powered Placement Management Platform', response.data)

    def test_02_student_login_and_dashboard(self):
        """Test student login and dashboard access"""
        response = self.client.post('/login', data={
            'identifier': 'student@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Alex Morgan', response.data)
        self.assertIn(b'Current CGPA', response.data)

    def test_03_ai_recommendation_and_eligibility(self):
        """Test AI matching logic and eligibility heuristics"""
        student = StudentProfile.query.filter_by(full_name='Alex Morgan').first()
        self.assertIsNotNone(student)

        jobs = Job.query.filter_by(is_active=True).all()
        self.assertTrue(len(jobs) > 0)

        # Calculate match for all jobs
        recommendations = recommender.get_recommendations(student, jobs, top_n=5)
        self.assertTrue(len(recommendations) > 0)
        
        top_rec = recommendations[0]
        self.assertIn('match_score', top_rec)
        self.assertIn('reasons', top_rec)
        self.assertTrue(top_rec['match_score'] > 50)
        print(f"Top recommendation: {top_rec['job'].title} with {top_rec['match_score']}% Match.")

    def test_04_admin_dashboard_and_api(self):
        """Test admin login and chart data REST endpoint"""
        # Login as Admin
        self.client.post('/login', data={
            'identifier': 'admin@example.com',
            'password': 'admin123'
        }, follow_redirects=True)

        # Check chart API
        response = self.client.get('/api/admin/chart-data')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('applications_by_company', data)
        self.assertIn('placement_status', data)
        self.assertIn('salary_distribution', data)

    def test_05_company_dashboard(self):
        """Test company recruiter access"""
        response = self.client.post('/login', data={
            'identifier': 'recruiter@google.com',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Google Recruiter Dashboard', response.data)

    def test_06_resume_parser(self):
        """Test resume skill extraction with sample tech text"""
        sample_text = "Experienced software engineer skilled in Python, React, SQL, Docker, AWS, and Machine Learning."
        skills = resume_parser.extract_skills(sample_text)
        self.assertIn('Python', skills)
        self.assertIn('React', skills)
        self.assertIn('SQL', skills)
        self.assertIn('Machine Learning', skills)
        print(f"Detected skills from resume sample: {skills}")

if __name__ == '__main__':
    unittest.main()
