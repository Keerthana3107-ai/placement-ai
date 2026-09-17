import os
import sys
from datetime import datetime, timedelta
from app import create_app
from models import db, User, StudentProfile, Skill, Project, Certification, Company, Job, Application, Interview, Notification

def seed_database():
    app = create_app()
    with app.app_context():
        print("Cleaning and recreating database...")
        db.drop_all()
        db.create_all()

        # ---------------------------------------------------------------------
        # 1. CREATE ADMIN USER
        # ---------------------------------------------------------------------
        admin = User(
            username="admin",
            email="admin@example.com",
            role="admin"
        )
        admin.set_password("admin123")
        db.session.add(admin)
        print("Created Admin: admin@example.com / admin123")

        # ---------------------------------------------------------------------
        # 2. CREATE COMPANIES & RECRUITER USERS
        # ---------------------------------------------------------------------
        companies_data = [
            {
                "name": "Google",
                "email": "recruiter@google.com",
                "username": "google_recruiter",
                "industry": "Internet & Cloud Technology",
                "location": "Bangalore / Hyderabad",
                "website": "https://careers.google.com",
                "logo_url": "https://upload.wikimedia.org/wikipedia/commons/2/2f/Google_2015_logo.svg",
                "description": "Google's mission is to organize the world's information and make it universally accessible and useful.",
                "recruiter_name": "Sundar Raman",
            },
            {
                "name": "Microsoft",
                "email": "recruiter@microsoft.com",
                "username": "microsoft_recruiter",
                "industry": "Software & Cloud Services",
                "location": "Hyderabad / Bangalore",
                "website": "https://careers.microsoft.com",
                "logo_url": "https://upload.wikimedia.org/wikipedia/commons/9/96/Microsoft_logo_%282012%29.svg",
                "description": "Empowering every person and organization on the planet to achieve more through Azure, AI, and modern productivity.",
                "recruiter_name": "Satya Priya",
            },
            {
                "name": "Amazon",
                "email": "recruiter@amazon.com",
                "username": "amazon_recruiter",
                "industry": "E-Commerce & Cloud Infrastructure",
                "location": "Bangalore / Chennai",
                "website": "https://amazon.jobs",
                "logo_url": "https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg",
                "description": "Earth's most customer-centric company, leading the frontier of distributed cloud architectures with AWS.",
                "recruiter_name": "Ananya Sharma",
            },
            {
                "name": "Deloitte",
                "email": "recruiter@deloitte.com",
                "username": "deloitte_recruiter",
                "industry": "Consulting & Technology Advisory",
                "location": "Mumbai / Gurgaon",
                "website": "https://www2.deloitte.com",
                "logo_url": "https://upload.wikimedia.org/wikipedia/commons/5/56/Deloitte.svg",
                "description": "Deloitte drives measurable and lasting results across consulting, cloud transformation, and enterprise analytics.",
                "recruiter_name": "Vikram Malhotra",
            },
            {
                "name": "TCS (Tata Consultancy Services)",
                "email": "recruiter@tcs.com",
                "username": "tcs_recruiter",
                "industry": "IT Services & Consulting",
                "location": "Pune / Chennai / Mumbai",
                "website": "https://www.tcs.com",
                "logo_url": "https://upload.wikimedia.org/wikipedia/commons/b/b1/Tata_Consultancy_Services_Logo.svg",
                "description": "Global leader in IT consulting and business solutions, fostering digital innovations with TCS Digital & Prime.",
                "recruiter_name": "Deepak Mehta",
            },
            {
                "name": "Infosys",
                "email": "recruiter@infosys.com",
                "username": "infosys_recruiter",
                "industry": "Next-Gen Digital Services",
                "location": "Bangalore / Mysore / Pune",
                "website": "https://www.infosys.com",
                "logo_url": "https://upload.wikimedia.org/wikipedia/commons/9/95/Infosys_logo.svg",
                "description": "Enabling clients in 50+ countries to navigate their digital transformation through AI, automation, and cloud.",
                "recruiter_name": "Pooja Hegde",
            }
        ]

        created_companies = {}
        for cdata in companies_data:
            rec_user = User(
                username=cdata['username'],
                email=cdata['email'],
                role="company"
            )
            rec_user.set_password("password123")
            db.session.add(rec_user)
            db.session.flush()

            comp = Company(
                user_id=rec_user.id,
                name=cdata['name'],
                industry=cdata['industry'],
                location=cdata['location'],
                website=cdata['website'],
                logo_url=cdata['logo_url'],
                description=cdata['description'],
                recruiter_name=cdata['recruiter_name'],
                recruiter_email=cdata['email']
            )
            db.session.add(comp)
            db.session.flush()
            created_companies[cdata['name']] = comp

        print(f"Created {len(created_companies)} Companies with recruiter logins.")

        # ---------------------------------------------------------------------
        # 3. CREATE JOB POSTINGS
        # ---------------------------------------------------------------------
        jobs_data = [
            {
                "company": "Google",
                "title": "Software Engineer (New Grad)",
                "description": "Design, develop, test, deploy, maintain, and improve large-scale distributed software applications. Work with cutting-edge microservice architectures and high-throughput systems.",
                "required_skills": "Python, Java, Data Structures, Algorithms, SQL, System Design",
                "min_cgpa": 8.0,
                "eligible_departments": "Computer Science, Information Technology",
                "graduation_year": 2026,
                "salary_package": "24 LPA",
                "salary_numeric": 24.0,
                "location": "Bangalore",
                "deadline": "2026-10-30",
                "openings": 8
            },
            {
                "company": "Google",
                "title": "Cloud Infrastructure Engineer",
                "description": "Collaborate with Google Cloud teams to develop scalable infrastructure, containerized deployments, and observability tools.",
                "required_skills": "Python, Linux, Docker, Kubernetes, GCP, Go, Git",
                "min_cgpa": 7.5,
                "eligible_departments": "Computer Science, Information Technology, Electronics",
                "graduation_year": 2026,
                "salary_package": "20 LPA",
                "salary_numeric": 20.0,
                "location": "Hyderabad",
                "deadline": "2026-11-15",
                "openings": 5
            },
            {
                "company": "Microsoft",
                "title": "Full Stack Software Engineer",
                "description": "Build high-impact web and backend services powering Microsoft 365 and Azure Developer Tools. Experience with modern web frameworks and REST APIs is required.",
                "required_skills": "JavaScript, TypeScript, React, Node.js, Python, SQL, HTML, CSS",
                "min_cgpa": 7.5,
                "eligible_departments": "Computer Science, Information Technology, Electronics",
                "graduation_year": 2026,
                "salary_package": "18 LPA",
                "salary_numeric": 18.0,
                "location": "Hyderabad",
                "deadline": "2026-10-25",
                "openings": 10
            },
            {
                "company": "Microsoft",
                "title": "Data & AI Associate Engineer",
                "description": "Work on applied machine learning pipelines, Azure Cognitive Services, and predictive models using Python, Scikit-learn, and Pandas.",
                "required_skills": "Python, Machine Learning, Scikit-learn, Pandas, NumPy, SQL, Data Science",
                "min_cgpa": 8.0,
                "eligible_departments": "Computer Science, Information Technology",
                "graduation_year": 2026,
                "salary_package": "19 LPA",
                "salary_numeric": 19.0,
                "location": "Bangalore",
                "deadline": "2026-11-05",
                "openings": 6
            },
            {
                "company": "Amazon",
                "title": "Software Development Engineer (SDE-1)",
                "description": "Develop mission-critical customer-facing services and distributed backend systems for AWS and global retail platform.",
                "required_skills": "Java, Python, Data Structures, Algorithms, Object-Oriented Programming, AWS, SQL",
                "min_cgpa": 7.0,
                "eligible_departments": "Computer Science, Information Technology, Electronics, Electrical",
                "graduation_year": 2026,
                "salary_package": "22 LPA",
                "salary_numeric": 22.0,
                "location": "Bangalore",
                "deadline": "2026-10-20",
                "openings": 12
            },
            {
                "company": "Deloitte",
                "title": "Technology Consultant (Analytics & Cloud)",
                "description": "Provide strategic consulting and enterprise system integrations. Analyze client business workflows and implement cloud-native databases.",
                "required_skills": "SQL, Python, Business Intelligence, Data Analysis, Excel, Cloud",
                "min_cgpa": 6.5,
                "eligible_departments": "Computer Science, Information Technology, Electronics, Mechanical, Civil",
                "graduation_year": 2026,
                "salary_package": "9.5 LPA",
                "salary_numeric": 9.5,
                "location": "Gurgaon / Mumbai",
                "deadline": "2026-11-10",
                "openings": 15
            },
            {
                "company": "TCS (Tata Consultancy Services)",
                "title": "TCS Digital - Full Stack Developer",
                "description": "High-growth digital engineering track for innovators. Work with modern enterprise stacks, microservices, and reactive frontends.",
                "required_skills": "Java, Python, Spring Boot, HTML, CSS, JavaScript, SQL",
                "min_cgpa": 7.0,
                "eligible_departments": "Computer Science, Information Technology, Electronics",
                "graduation_year": 2026,
                "salary_package": "7.5 LPA",
                "salary_numeric": 7.5,
                "location": "Pune / Chennai",
                "deadline": "2026-11-20",
                "openings": 25
            },
            {
                "company": "Infosys",
                "title": "Specialist Programmer (Power Programmer)",
                "description": "Competitive coding and engineering track focused on algorithmic problem solving, cloud development, and AI engineering.",
                "required_skills": "Python, Java, Data Structures, Algorithms, REST API, Git",
                "min_cgpa": 6.5,
                "eligible_departments": "Computer Science, Information Technology, Electronics, Mechanical",
                "graduation_year": 2026,
                "salary_package": "9.0 LPA",
                "salary_numeric": 9.0,
                "location": "Bangalore / Pune",
                "deadline": "2026-11-30",
                "openings": 20
            },
            {
                "company": "Infosys",
                "title": "Systems Engineer",
                "description": "Comprehensive IT lifecycle operations, application maintenance, quality assurance, and automated deployment.",
                "required_skills": "C, C++, Java, Python, SQL, HTML, CSS",
                "min_cgpa": 6.0,
                "eligible_departments": "Computer Science, Information Technology, Electronics, Electrical, Mechanical, Civil",
                "graduation_year": 2026,
                "salary_package": "4.5 LPA",
                "salary_numeric": 4.5,
                "location": "Mysore / Chennai",
                "deadline": "2026-12-15",
                "openings": 50
            }
        ]

        created_jobs = []
        for jdata in jobs_data:
            comp = created_companies[jdata['company']]
            job = Job(
                company_id=comp.id,
                title=jdata['title'],
                description=jdata['description'],
                required_skills=jdata['required_skills'],
                min_cgpa=jdata['min_cgpa'],
                eligible_departments=jdata['eligible_departments'],
                graduation_year=jdata['graduation_year'],
                salary_package=jdata['salary_package'],
                salary_numeric=jdata['salary_numeric'],
                location=jdata['location'],
                deadline=jdata['deadline'],
                openings=jdata['openings'],
                is_active=True
            )
            db.session.add(job)
            db.session.flush()
            created_jobs.append(job)

        print(f"Created {len(created_jobs)} Job Postings.")

        # ---------------------------------------------------------------------
        # 4. CREATE STUDENTS, SKILLS, PROJECTS & RESUMES
        # ---------------------------------------------------------------------
        # Create a sample PDF resume file
        resume_dir = app.config['UPLOAD_FOLDER']
        os.makedirs(resume_dir, exist_ok=True)
        demo_resume_path = os.path.join(resume_dir, "student_1_alex_resume.pdf")
        
        # Write a dummy valid PDF or plain text PDF placeholder
        with open(demo_resume_path, "wb") as f:
            f.write(b"%PDF-1.4\n%Demo PDF Resume for Alex Morgan\nSkills: Python, JavaScript, React, SQL, Machine Learning, Flask, Git, Docker\n%%EOF")

        students_data = [
            {
                "username": "alex_student",
                "email": "student@example.com",
                "name": "Alex Morgan",
                "department": "Computer Science",
                "cgpa": 8.85,
                "tenth": 92.5,
                "twelfth": 91.0,
                "phone": "+91 98765 43210",
                "status": "Unplaced",
                "resume": "student_1_alex_resume.pdf",
                "skills": [
                    ("Python", "Advanced"),
                    ("JavaScript", "Advanced"),
                    ("SQL", "Intermediate"),
                    ("React", "Intermediate"),
                    ("Machine Learning", "Intermediate"),
                    ("Flask", "Advanced"),
                    ("Git", "Advanced"),
                    ("HTML", "Advanced"),
                    ("CSS", "Intermediate"),
                    ("Data Structures", "Advanced")
                ],
                "projects": [
                    ("Campus Placement Portal", "Full-stack web application with AI recommendation engine and automated eligibility verification.", "Python, Flask, SQLite, Bootstrap, Scikit-learn"),
                    ("Real-Time Stock Market Predictor", "Predictive time-series model utilizing LSTM and Random Forest to forecast equity trends.", "Python, Pandas, Scikit-learn, TensorFlow")
                ],
                "certifications": [
                    ("AWS Certified Cloud Practitioner", "Amazon Web Services", 2025),
                    ("Machine Learning Specialization", "DeepLearning.AI / Coursera", 2024)
                ]
            },
            {
                "username": "priya_sharma",
                "email": "priya@example.com",
                "name": "Priya Sharma",
                "department": "Computer Science",
                "cgpa": 9.40,
                "tenth": 95.0,
                "twelfth": 94.2,
                "phone": "+91 98111 22334",
                "status": "Placed",
                "placed_company": "Google",
                "placed_package": 24.0,
                "resume": None,
                "skills": [
                    ("Java", "Advanced"),
                    ("Python", "Advanced"),
                    ("Data Structures", "Advanced"),
                    ("Algorithms", "Advanced"),
                    ("System Design", "Intermediate"),
                    ("SQL", "Intermediate")
                ],
                "projects": [
                    ("Distributed File Storage", "Fault-tolerant distributed key-value store with consensus protocol.", "Java, gRPC, Docker")
                ],
                "certifications": [
                    ("Google Cloud Professional Architect", "Google Cloud", 2025)
                ]
            },
            {
                "username": "rohit_verma",
                "email": "rohit@example.com",
                "name": "Rohit Verma",
                "department": "Information Technology",
                "cgpa": 7.80,
                "tenth": 85.0,
                "twelfth": 83.5,
                "phone": "+91 98222 33445",
                "status": "Unplaced",
                "resume": None,
                "skills": [
                    ("JavaScript", "Advanced"),
                    ("React", "Advanced"),
                    ("Node.js", "Intermediate"),
                    ("TypeScript", "Intermediate"),
                    ("HTML", "Advanced"),
                    ("CSS", "Advanced"),
                    ("SQL", "Beginner")
                ],
                "projects": [
                    ("E-Commerce Dashboard", "Interactive admin dashboard with real-time sales reporting and order status updates.", "React, Node.js, Express, MongoDB")
                ],
                "certifications": [
                    ("Meta Front-End Developer Professional", "Meta / Coursera", 2024)
                ]
            },
            {
                "username": "neha_patel",
                "email": "neha@example.com",
                "name": "Neha Patel",
                "department": "Electronics",
                "cgpa": 8.10,
                "tenth": 88.0,
                "twelfth": 86.0,
                "phone": "+91 98333 44556",
                "status": "Placed",
                "placed_company": "Microsoft",
                "placed_package": 18.0,
                "resume": None,
                "skills": [
                    ("C++", "Advanced"),
                    ("Python", "Intermediate"),
                    ("Linux", "Intermediate"),
                    ("SQL", "Intermediate"),
                    ("Data Structures", "Intermediate")
                ],
                "projects": [
                    ("Embedded IoT Smart Health Monitor", "Real-time vitals tracking telemetry system with MQTT broker.", "C++, Python, Raspberry Pi")
                ],
                "certifications": [
                    ("Microsoft Azure Fundamentals AZ-900", "Microsoft", 2024)
                ]
            },
            {
                "username": "karan_singh",
                "email": "karan@example.com",
                "name": "Karan Singh",
                "department": "Mechanical",
                "cgpa": 6.85,
                "tenth": 78.0,
                "twelfth": 76.5,
                "phone": "+91 98444 55667",
                "status": "Unplaced",
                "resume": None,
                "skills": [
                    ("Python", "Beginner"),
                    ("SQL", "Intermediate"),
                    ("Data Analysis", "Intermediate"),
                    ("Excel", "Advanced")
                ],
                "projects": [
                    ("Manufacturing Supply Chain Optimizer", "Inventory bottleneck simulation using linear programming.", "Python, Excel Solver")
                ],
                "certifications": [
                    ("Google Data Analytics Certificate", "Google", 2024)
                ]
            }
        ]

        created_students = []
        for sdata in students_data:
            s_user = User(
                username=sdata['username'],
                email=sdata['email'],
                role="student"
            )
            s_user.set_password("password123")
            db.session.add(s_user)
            db.session.flush()

            profile = StudentProfile(
                user_id=s_user.id,
                full_name=sdata['name'],
                phone=sdata['phone'],
                department=sdata['department'],
                cgpa=sdata['cgpa'],
                tenth_pct=sdata['tenth'],
                twelfth_pct=sdata['twelfth'],
                resume_filename=sdata['resume'],
                placement_status=sdata['status'],
                placed_company=sdata.get('placed_company'),
                placed_package=sdata.get('placed_package'),
                graduation_year=2026
            )
            db.session.add(profile)
            db.session.flush()

            # Add skills
            for s_name, prof in sdata['skills']:
                db.session.add(Skill(student_id=profile.id, skill_name=s_name, proficiency=prof))

            # Add projects
            for p_title, p_desc, p_stack in sdata['projects']:
                db.session.add(Project(student_id=profile.id, title=p_title, description=p_desc, tech_stack=p_stack))

            # Add certifications
            for c_title, c_issuer, c_year in sdata['certifications']:
                db.session.add(Certification(student_id=profile.id, title=c_title, issuer=c_issuer, issue_year=c_year))

            created_students.append(profile)

        print(f"Created {len(created_students)} Student Profiles with skills, projects, and certifications.")

        # ---------------------------------------------------------------------
        # 5. CREATE APPLICATIONS & INTERVIEWS
        # ---------------------------------------------------------------------
        alex = created_students[0]
        priya = created_students[1]
        rohit = created_students[2]
        neha = created_students[3]

        google_swe = created_jobs[0]
        msft_fullstack = created_jobs[2]
        msft_ai = created_jobs[3]
        amzn_sde = created_jobs[4]
        deloitte_consultant = created_jobs[5]

        # Alex Morgan's applications
        app_alex_msft_ai = Application(
            student_id=alex.id,
            job_id=msft_ai.id,
            status="Interview Scheduled",
            remarks="Excellent profile match with Python and Scikit-learn portfolio."
        )
        app_alex_google = Application(
            student_id=alex.id,
            job_id=google_swe.id,
            status="Under Review",
            remarks="Application screened. Meets CGPA cutoff."
        )
        app_alex_amzn = Application(
            student_id=alex.id,
            job_id=amzn_sde.id,
            status="Shortlisted",
            remarks="Online coding round cleared with 100% test cases."
        )
        db.session.add_all([app_alex_msft_ai, app_alex_google, app_alex_amzn])
        db.session.flush()

        # Interview for Alex
        interview_date = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
        alex_interview = Interview(
            application_id=app_alex_msft_ai.id,
            student_id=alex.id,
            company_id=msft_ai.company_id,
            job_id=msft_ai.id,
            interview_date=interview_date,
            interview_time="10:30 AM",
            mode="Online (Microsoft Teams)",
            meeting_link="https://teams.microsoft.com/l/meetup-join/19-sample-msft-interview",
            round_name="Technical Round 1: Machine Learning & Python",
            notes="Please prepare to discuss your Stock Market Predictor project and system architecture."
        )
        db.session.add(alex_interview)

        # Other student applications
        app_priya_google = Application(
            student_id=priya.id,
            job_id=google_swe.id,
            status="Selected",
            remarks="Outstanding problem solving and distributed system design skills."
        )
        app_rohit_msft = Application(
            student_id=rohit.id,
            job_id=msft_fullstack.id,
            status="Shortlisted",
            remarks="Strong React frontend portfolio."
        )
        app_neha_msft = Application(
            student_id=neha.id,
            job_id=msft_fullstack.id,
            status="Selected",
            remarks="Offered position in Core Cloud platform."
        )
        db.session.add_all([app_priya_google, app_rohit_msft, app_neha_msft])

        # Notifications for Alex
        notif1 = Notification(
            user_id=alex.user_id,
            title="Interview Scheduled!",
            message=f"Your Technical Round 1 with Microsoft is scheduled for {interview_date} at 10:30 AM.",
            link="/student/interviews"
        )
        notif2 = Notification(
            user_id=alex.user_id,
            title="Application Shortlisted",
            message="Amazon SDE-1 has shortlisted your profile for the next evaluation stage.",
            link="/student/applications"
        )
        notif3 = Notification(
            user_id=alex.user_id,
            title="Recommended Job Matches",
            message="3 new placement opportunities matching your technical skills have opened up.",
            link="/student/recommendations"
        )
        db.session.add_all([notif1, notif2, notif3])

        db.session.commit()
        print("\nSUCCESS! Database seeded successfully.")
        print("--------------------------------------------------")
        print("DEMO CREDENTIALS:")
        print("1. Student Account:")
        print("   Email:    student@example.com")
        print("   Password: password123")
        print("2. Admin / Placement Officer Account:")
        print("   Email:    admin@example.com")
        print("   Password: admin123")
        print("3. Company / Recruiter Account:")
        print("   Email:    recruiter@google.com")
        print("   Password: password123")
        print("--------------------------------------------------")

if __name__ == '__main__':
    seed_database()
