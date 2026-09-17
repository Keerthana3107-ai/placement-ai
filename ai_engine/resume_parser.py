import re
import os

# Extensive catalog of industry technical skills
TECH_SKILLS_CATALOG = {
    # Programming Languages
    "Python": [r"\bpython\b", r"\bpython3\b"],
    "Java": [r"\bjava\b(?!script)"],
    "C": [r"(?<!\w)c(?!\w|[+#])"],
    "C++": [r"\bc\+\+\b", r"\bcpp\b"],
    "C#": [r"\bc#\b", r"\bcsharp\b"],
    "JavaScript": [r"\bjavascript\b", r"\bjs\b"],
    "TypeScript": [r"\btypescript\b", r"\bts\b"],
    "PHP": [r"\bphp\b"],
    "Ruby": [r"\bruby\b"],
    "Go": [r"\bgolang\b", r"(?<!\w)go(?!\w)"],
    "Rust": [r"\brust\b"],
    "Kotlin": [r"\bkotlin\b"],
    "Swift": [r"\bswift\b"],
    "R": [r"(?<!\w)r(?!\w)"],
    
    # Web & Frontend
    "HTML": [r"\bhtml5?\b"],
    "CSS": [r"\bcss3?\b", r"\btailwind\b", r"\bbootstrap\b"],
    "React": [r"\breact(\.?js)?\b"],
    "Angular": [r"\bangular(\.?js)?\b"],
    "Vue.js": [r"\bvue(\.?js)?\b"],
    "Next.js": [r"\bnext(\.?js)?\b"],
    "Node.js": [r"\bnode(\.?js)?\b"],
    "Express": [r"\bexpress(\.?js)?\b"],
    "Flask": [r"\bflask\b"],
    "Django": [r"\bdjango\b"],
    "Spring Boot": [r"\bspring boot\b", r"\bspring\b"],
    "FastAPI": [r"\bfastapi\b"],
    "ASP.NET": [r"\basp\.net\b", r"\b\.net\b"],
    
    # Databases & Storage
    "SQL": [r"\bsql\b"],
    "MySQL": [r"\bmysql\b"],
    "PostgreSQL": [r"\bpostgresql\b", r"\bpostgres\b"],
    "MongoDB": [r"\bmongodb\b", r"\bmongo\b"],
    "SQLite": [r"\bsqlite\b"],
    "Redis": [r"\bredis\b"],
    "Oracle": [r"\boracle\b"],
    
    # Cloud & DevOps
    "AWS": [r"\baws\b", r"\bamazon web services\b"],
    "Azure": [r"\bazure\b"],
    "GCP": [r"\bgcp\b", r"\bgoogle cloud\b"],
    "Docker": [r"\bdocker\b"],
    "Kubernetes": [r"\bkubernetes\b", r"\bk8s\b"],
    "Git": [r"\bgit\b", r"\bgithub\b", r"\bgitlab\b"],
    "CI/CD": [r"\bci/cd\b", r"\bjenkins\b"],
    "Linux": [r"\blinux\b", r"\bunix\b", r"\bbash\b"],
    
    # AI / Machine Learning & Data Science
    "Machine Learning": [r"\bmachine learning\b", r"\bml\b"],
    "Deep Learning": [r"\bdeep learning\b", r"\bdl\b"],
    "Data Science": [r"\bdata science\b"],
    "Artificial Intelligence": [r"\bartificial intelligence\b", r"\bai\b"],
    "TensorFlow": [r"\btensorflow\b"],
    "PyTorch": [r"\bpytorch\b"],
    "Scikit-learn": [r"\bscikit-learn\b", r"\bsklearn\b"],
    "Pandas": [r"\bpandas\b"],
    "NumPy": [r"\bnumpy\b"],
    "NLP": [r"\bnlp\b", r"\bnatural language processing\b"],
    "Computer Vision": [r"\bcomputer vision\b", r"\bopencv\b"],
    
    # Core Concepts & Architecture
    "Data Structures": [r"\bdata structures\b", r"\bdsa\b"],
    "Algorithms": [r"\balgorithms?\b"],
    "Object-Oriented Programming": [r"\boop\b", r"\boops\b", r"\bobject oriented\b"],
    "REST API": [r"\brest(ful)? api\b", r"\brest\b"],
    "GraphQL": [r"\bgraphql\b"],
    "Microservices": [r"\bmicroservices\b"],
    "System Design": [r"\bsystem design\b"]
}


class ResumeParser:
    """
    Robust resume skill extraction engine using pypdf, PyPDF2, and regex matching.
    """

    @staticmethod
    def extract_text_from_pdf(file_path):
        """
        Extract text from a PDF file with multiple resilient fallbacks.
        """
        if not os.path.exists(file_path):
            return "", "File does not exist."

        text = ""
        # 1. Try modern pypdf
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            if text.strip():
                return text, None
        except Exception:
            pass

        # 2. Try PyPDF2
        try:
            import PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            if text.strip():
                return text, None
        except Exception:
            pass

        # 3. Resilient binary stream text scanner fallback
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                # Find all printable ASCII substrings of length >= 3
                raw_strings = re.findall(rb'[A-Za-z0-9\+\#\.\,\s\:\-\/]{3,}', content)
                extracted = " ".join([s.decode('utf-8', errors='ignore') for s in raw_strings])
                if len(extracted.strip()) > 50:
                    return extracted, None
        except Exception as e:
            return "", f"Could not read PDF: {str(e)}"

        return "", "Could not extract readable text from PDF. The document may be an image scan or password-protected."

    @classmethod
    def extract_skills(cls, text):
        """
        Identify technical skills from text using regex catalog.
        Returns: list of matched skill names.
        """
        if not text:
            return []

        matched_skills = []
        lower_text = text.lower()

        for skill_name, patterns in TECH_SKILLS_CATALOG.items():
            for pattern in patterns:
                if re.search(pattern, lower_text, re.IGNORECASE):
                    matched_skills.append(skill_name)
                    break

        return sorted(matched_skills)

    @classmethod
    def analyze_resume(cls, file_path):
        """
        Full pipeline: text extraction + skill analysis.
        Returns: { 'success': bool, 'text': str, 'skills': list, 'error': str }
        """
        text, error = cls.extract_text_from_pdf(file_path)
        if error and not text:
            return {
                'success': False,
                'text': '',
                'skills': [],
                'error': error
            }

        skills = cls.extract_skills(text)
        return {
            'success': True,
            'text': text[:2000],  # preview of first 2000 chars
            'skills': skills,
            'error': None
        }


resume_parser = ResumeParser()
