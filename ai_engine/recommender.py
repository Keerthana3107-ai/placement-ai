import os
import re
import joblib
import numpy as np

# Try importing scikit-learn
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class PlacementRecommender:
    """
    Explainable AI/ML Job Recommendation & Eligibility Engine.
    Uses Scikit-learn TfidfVectorizer and Cosine Similarity combined with
    deterministic academic eligibility heuristics.
    """
    
    def __init__(self, model_dir=None):
        self.model_dir = model_dir or os.path.join(os.path.dirname(__file__), 'models')
        os.makedirs(self.model_dir, exist_ok=True)
        self.vectorizer_path = os.path.join(self.model_dir, 'skill_vectorizer.joblib')
        self._init_vectorizer()

    def _init_vectorizer(self):
        """Initialize or load cached Scikit-learn TfidfVectorizer using Joblib."""
        if not SKLEARN_AVAILABLE:
            self.vectorizer = None
            return

        if os.path.exists(self.vectorizer_path):
            try:
                self.vectorizer = joblib.load(self.vectorizer_path)
                return
            except Exception:
                pass

        # Train a default baseline vocabulary on common technical skill tokens
        baseline_corpus = [
            "python java c c++ c# ruby go rust php javascript typescript html css",
            "react angular vue node express flask django spring boot asp.net",
            "sql mysql postgresql sqlite mongodb redis oracle cassandra",
            "aws azure gcp docker kubernetes terraform devops git linux",
            "machine learning deep learning tensorflow pytorch scikit-learn nlp computer vision data science pandas numpy",
            "data structures algorithms system design object oriented programming agile rest api graphql",
            "software engineering full stack development cloud computing microservices"
        ]
        try:
            self.vectorizer = TfidfVectorizer(token_pattern=r'(?u)\b[a-zA-Z0-9#\+\.-]+\b', lowercase=True)
            self.vectorizer.fit(baseline_corpus)
            joblib.dump(self.vectorizer, self.vectorizer_path)
        except Exception:
            self.vectorizer = None

    def _normalize_text(self, text):
        if not text:
            return ""
        return re.sub(r'[,;/\|]', ' ', text.lower()).strip()

    def _calculate_text_similarity(self, text1, text2):
        """Calculate TF-IDF Cosine similarity between two text strings using Scikit-learn."""
        if not text1 or not text2:
            return 0.0

        if SKLEARN_AVAILABLE:
            try:
                # Use dynamic vectorizer to fit both texts precisely
                vec = TfidfVectorizer(token_pattern=r'(?u)\b[a-zA-Z0-9#\+\.-]+\b', lowercase=True)
                tfidf_matrix = vec.fit_transform([text1, text2])
                sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                return float(sim)
            except Exception:
                pass

        # Fallback Jaccard token similarity if sklearn encounters any anomaly
        tokens1 = set(re.findall(r'[a-zA-Z0-9#\+\.-]+', text1.lower()))
        tokens2 = set(re.findall(r'[a-zA-Z0-9#\+\.-]+', text2.lower()))
        if not tokens1 or not tokens2:
            return 0.0
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        return len(intersection) / len(union) if union else 0.0

    def check_eligibility(self, student, job):
        """
        Check hard eligibility criteria:
        1. CGPA >= Job Minimum CGPA
        2. Student Department in Job Eligible Departments
        3. Graduation Year matches Job requirement
        Returns: (is_eligible: bool, passed_reasons: list, failure_reasons: list)
        """
        passed_reasons = []
        failure_reasons = []

        if not student:
            return False, [], ["Student profile not found."]

        # 1. CGPA check
        student_cgpa = float(student.cgpa or 0.0)
        job_min_cgpa = float(job.min_cgpa or 0.0)
        
        if student_cgpa >= job_min_cgpa:
            passed_reasons.append(f"CGPA ({student_cgpa:.2f}) satisfies minimum requirement of {job_min_cgpa:.2f}.")
        else:
            diff = job_min_cgpa - student_cgpa
            failure_reasons.append(f"CGPA ({student_cgpa:.2f}) is below the required {job_min_cgpa:.2f} (short by {diff:.2f}).")

        # 2. Department check
        eligible_depts = [d.strip().lower() for d in (job.eligible_departments or '').split(',') if d.strip()]
        student_dept = (student.department or '').strip().lower()
        
        dept_match = False
        if not eligible_depts or 'all' in eligible_depts or 'any' in eligible_depts:
            dept_match = True
        else:
            for dept in eligible_depts:
                if dept in student_dept or student_dept in dept:
                    dept_match = True
                    break

        if dept_match:
            passed_reasons.append(f"Department ({student.department}) is eligible for this drive.")
        else:
            allowed_str = ", ".join([d.strip() for d in (job.eligible_departments or '').split(',')])
            failure_reasons.append(f"Department '{student.department}' is not in the eligible list: {allowed_str}.")

        # 3. Graduation Year check
        if job.graduation_year:
            student_grad_year = int(student.graduation_year or 0)
            job_grad_year = int(job.graduation_year)
            if student_grad_year == job_grad_year:
                passed_reasons.append(f"Graduation year ({student_grad_year}) matches the batch requirement ({job_grad_year}).")
            else:
                failure_reasons.append(f"Batch mismatch: Job is for {job_grad_year} batch, you are {student_grad_year} batch.")

        is_eligible = len(failure_reasons) == 0
        return is_eligible, passed_reasons, failure_reasons

    def calculate_match(self, student, job):
        """
        Calculate an explainable multi-factor match score (0-100%):
        - Skill Match (40%): Direct overlap + Scikit-Learn TF-IDF Cosine Similarity
        - CGPA Compatibility (25%): Proportional score with bonus/penalty
        - Department Compatibility (20%): Branch match
        - Projects & Certifications (15%): NLP relevance of student projects & certs to job description
        """
        if not student or not job:
            return {
                'match_score': 0,
                'is_eligible': False,
                'reasons': [],
                'missing_reasons': ['Missing student or job data.'],
                'matched_skills': [],
                'unmatched_skills': []
            }

        # 1. Eligibility evaluation
        is_eligible, passed_eligibility, failure_reasons = self.check_eligibility(student, job)

        # 2. Skill Matching (Weight: 40%)
        student_skills = [s.strip().lower() for s in student.get_skill_names()]
        job_skills = [s.strip().lower() for s in job.get_required_skills_list()]
        
        matched_skills_list = []
        unmatched_skills_list = []
        
        for js in job_skills:
            # Check exact match or substring match
            found = False
            for ss in student_skills:
                if js == ss or js in ss or ss in js:
                    matched_skills_list.append(js)
                    found = True
                    break
            if not found:
                unmatched_skills_list.append(js)

        total_job_skills = max(len(job_skills), 1)
        direct_skill_ratio = len(matched_skills_list) / total_job_skills

        # Compute TF-IDF similarity between full skill strings
        student_skill_str = " ".join(student_skills)
        job_skill_str = " ".join(job_skills)
        tfidf_skill_sim = self._calculate_text_similarity(student_skill_str, job_skill_str)
        
        # Combine direct match with vector similarity
        skill_score = (direct_skill_ratio * 0.7) + (tfidf_skill_sim * 0.3)
        skill_score = min(max(skill_score, 0.0), 1.0)

        # 3. CGPA Compatibility (Weight: 25%)
        student_cgpa = float(student.cgpa or 0.0)
        job_min_cgpa = float(job.min_cgpa or 6.0)
        
        if student_cgpa >= job_min_cgpa:
            # Full base score plus small bonus for high CGPA (up to 10.0)
            cgpa_score = 0.85 + (min(student_cgpa - job_min_cgpa, 2.0) / 2.0) * 0.15
        else:
            # Scaled penalty if below
            cgpa_score = max(0.0, (student_cgpa / max(job_min_cgpa, 1.0)) * 0.5)

        # 4. Department Compatibility (Weight: 20%)
        dept_eligible, _, _ = self.check_eligibility(student, job)
        dept_score = 1.0 if dept_eligible else 0.2

        # 5. Project & Certification Relevance (Weight: 15%)
        project_text = " ".join([f"{p.title} {p.description} {p.tech_stack or ''}" for p in student.projects])
        cert_text = " ".join([f"{c.title} {c.issuer}" for c in student.certifications])
        combined_student_exp = f"{project_text} {cert_text}".strip()
        job_full_desc = f"{job.title} {job.description} {job.required_skills}"
        
        project_score = 0.0
        if combined_student_exp:
            project_score = self._calculate_text_similarity(combined_student_exp, job_full_desc)
            # Boost if student has projects
            if len(student.projects) > 0:
                project_score = max(project_score, 0.4)
        else:
            project_score = 0.1

        # Calculate weighted final score (0 - 100)
        raw_score = (
            (skill_score * 0.40) +
            (cgpa_score * 0.25) +
            (dept_score * 0.20) +
            (project_score * 0.15)
        ) * 100.0

        final_match_score = int(round(min(max(raw_score, 5.0), 99.0)))

        # Generate Explainable Reasons
        reasons = []
        missing_reasons = []

        # Skill explanation
        if matched_skills_list:
            display_matched = [s.title() for s in matched_skills_list[:4]]
            reasons.append(f"Matched {len(matched_skills_list)} required skill(s): {', '.join(display_matched)}.")
        if unmatched_skills_list:
            display_unmatched = [s.title() for s in unmatched_skills_list[:3]]
            missing_reasons.append(f"Missing skill(s): {', '.join(display_unmatched)}.")

        # CGPA explanation
        if student_cgpa >= job_min_cgpa:
            reasons.append(f"CGPA of {student_cgpa:.2f} satisfies the minimum cut-off ({job_min_cgpa:.2f}).")
        else:
            missing_reasons.append(f"CGPA ({student_cgpa:.2f}) is below the required {job_min_cgpa:.2f}.")

        # Department explanation
        if dept_score > 0.5:
            reasons.append(f"Your branch ({student.department}) is directly eligible for this recruitment drive.")
        else:
            missing_reasons.append(f"Your branch ({student.department}) is outside the preferred target departments.")

        # Project / Experience explanation
        if len(student.projects) > 0 and project_score > 0.3:
            reasons.append(f"Your project portfolio aligns well with the role requirements.")
        elif len(student.projects) == 0:
            missing_reasons.append("Adding relevant projects to your profile will boost your match score.")

        return {
            'match_score': final_match_score,
            'is_eligible': is_eligible,
            'reasons': reasons,
            'missing_reasons': missing_reasons,
            'matched_skills': [s.title() for s in matched_skills_list],
            'unmatched_skills': [s.title() for s in unmatched_skills_list],
            'factors': {
                'skills': int(round(skill_score * 100)),
                'cgpa': int(round(cgpa_score * 100)),
                'department': int(round(dept_score * 100)),
                'projects': int(round(project_score * 100))
            }
        }

    def get_recommendations(self, student, jobs, top_n=10, eligible_only=False):
        """
        Rank a collection of jobs for a given student based on match score.
        """
        ranked_jobs = []
        for job in jobs:
            match_data = self.calculate_match(student, job)
            if eligible_only and not match_data['is_eligible']:
                continue
            
            ranked_jobs.append({
                'job': job,
                'match_score': match_data['match_score'],
                'is_eligible': match_data['is_eligible'],
                'reasons': match_data['reasons'],
                'missing_reasons': match_data['missing_reasons'],
                'matched_skills': match_data['matched_skills'],
                'unmatched_skills': match_data['unmatched_skills'],
                'factors': match_data['factors']
            })

        # Sort descending by match score, prioritizing eligible ones
        ranked_jobs.sort(key=lambda x: (1 if x['is_eligible'] else 0, x['match_score']), reverse=True)
        return ranked_jobs[:top_n]


# Singleton instance
recommender = PlacementRecommender()
