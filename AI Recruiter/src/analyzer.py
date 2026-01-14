import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class BaseAnalyzer:
    """Interface for all analysis engines."""
    def analyze(self, resume_text, job_description, essential_skills=None):
        raise NotImplementedError

class KeywordAnalyzer(BaseAnalyzer):
    """
    Rule-Based Analyzer using keyword matching.
    No API Key required. Fast and Free.
    """
    def analyze(self, resume_text, job_description, essential_skills=None):
        # 1. Basic Cleaning
        resume_tokens = set(re.findall(r'\b[a-zA-Z0-9+#.]+\b', resume_text.lower()))
        jd_tokens = set(re.findall(r'\b[a-zA-Z0-9+#.]+\b', job_description.lower()))
        
        # 2. Extract Common Skills (Comprehensive Dictionary)
        # Expanded to cover Tech, Business, Finance, Design, and Soft Skills
        known_skills = {
            # --- Software Engineering & Tech ---
            "python", "java", "c++", "c#", ".net", "javascript", "typescript", "html", "css",
            "react", "angular", "vue", "node.js", "django", "flask", "fastapi", "spring boot",
            "sql", "mysql", "postgresql", "mongodb", "redis", "oracle", "nosql",
            "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "terraform", "ansible",
            "git", "github", "gitlab", "linux", "unix", "bash", "shell scripting",
            "rest api", "graphql", "microservices", "serverless", "agile", "scrum", "kanban",
            "machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch",
            "data analysis", "data science", "pandas", "numpy", "matplotlib", "tableau", "power bi",
            "big data", "hadoop", "spark", "kafka", "elasticsearch", "airflow",
            "cybersecurity", "network security", "penetration testing", "ethical hacking",
            "mobile development", "android", "ios", "swift", "kotlin", "flutter", "react native",

            # --- Business, Marketing & Sales ---
            "marketing", "digital marketing", "seo", "sem", "content marketing", "social media",
            "google analytics", "facebook ads", "google ads", "email marketing", "crm", "salesforce",
            "hubspot", "b2b", "b2c", "sales", "business development", "account management",
            "negotiation", "lead generation", "market research", "branding", "public relations",
            "copywriting", "blogging", "storytelling", "video editing",

            # --- Finance & Accounting ---
            "accounting", "finance", "auditing", "bookkeeping", "taxation", "financial analysis",
            "budgeting", "forecasting", "financial reporting", "excel", "sap", "oracle erp",
            "quickbooks", "xero", "ifrs", "gaap", "investment", "risk management", "compliance",

            # --- HR & Management ---
            "human resources", "recruitment", "talent acquisition", "onboarding", "employee relations",
            "payroll", "performance management", "training", "development", "hris", "workday",
            "project management", "product management", "jira", "asana", "trello", "confluence",
            "stakeholder management", "strategic planning", "operations", "supply chain", "logistics",

            # --- Design & Creative ---
            "graphic design", "ui design", "ux design", "web design", "adobe creative suite",
            "photoshop", "illustrator", "indesign", "figma", "sketch", "invision", "prototyping",
            "wireframing", "user research", "usability testing", "typography", "color theory",

            # --- Soft Skills & General ---
            "communication", "teamwork", "leadership", "problem solving", "critical thinking",
            "time management", "adaptability", "creativity", "emotional intelligence",
            "presentation", "public speaking", "collaboration", "mentoring", "coaching",
            "english", "thai", "japanese", "chinese", "mandarin", "german", "french"
        }
        
        # Refine known skills with what's asked in JD
        # If essential_skills provided, ensure they are in the required set
        required_skills = sorted(list(known_skills.intersection(jd_tokens)))
        
        if essential_skills:
             # Normalize essential skills
             essential_tokens = {s.lower() for s in essential_skills}
             # Add essential skills to required if not already there (assuming they are valid requirements)
             required_skills = sorted(list(set(required_skills).union(essential_tokens)))

        found_skills = sorted(list(known_skills.intersection(resume_tokens)))
        
        # 3. Calculate Weighted Score
        if not required_skills:
            match_score = 0
        else:
            base_matches = 0
            total_weight = 0
            
            for skill in required_skills:
                weight = 1
                if essential_skills and skill in [s.lower() for s in essential_skills]:
                    weight = 2 # Double points for essential skills
                
                total_weight += weight
                
                if skill in found_skills:
                    base_matches += weight
            
            if total_weight > 0:
                match_score = int((base_matches / total_weight) * 100)
            else:
                match_score = 0
            
        # 4. Identify Gaps
        missing_skills = sorted(list(set(required_skills) - set(found_skills)))

        # 5. Predict Seniority
        predicted_level = self.predict_seniority(resume_text.lower())
        
        # 6. Generate Static Questions based on missing skills
        questions = []
        if missing_skills:
            questions.append(f"Can you explain your experience with {missing_skills[0]}?")
            questions.append(f"Have you ever worked on a project requiring {missing_skills[-1]}?")
        questions.append("Describe a challenging technical problem you solved recently.")
        
        result = {
            "candidate_summary": "Analysis generated by Rule-Based Engine. (Keyword Matching)",
            "key_skills": found_skills,
            "match_score": match_score,
            "missing_skills": missing_skills,
            "seniority": predicted_level,
            "interview_questions": questions
        }
        return json.dumps(result)

    def predict_seniority(self, text):
        """Estimate seniority based on keywords."""
        levels = {
            "Executive (C-Level/VP)": ["chief", "cto", "ceo", "cfo", "vp", "president", "director of", "head of", "executive"],
            "Manager": ["manager", "lead", "principal", "architect", "management", "strategy"],
            "Senior": ["senior", "expert", "specialist", "advanced", "5+ years", "years of experience"],
            "Mid-Level": ["mid-level", "intermediate", "officer", "associate", "2-5 years"],
            "Junior/Entry": ["junior", "intern", "trainee", "entry-level", "fresh graduate", "student", "0-2 years"]
        }
        
        for level, keywords in levels.items():
            for kw in keywords:
                if kw in text:
                    return level
        return "Not Specified"

class GeminiAnalyzer(BaseAnalyzer):
    """
    Advanced Analyzer using Google's Gemini LLM.
    Requires GOOGLE_API_KEY.
    """
    def __init__(self, model_name='gemini-pro'):
        self.model_name = model_name
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            
    def analyze(self, resume_text, job_description, essential_skills=None):
        if not os.getenv("GOOGLE_API_KEY"):
             return json.dumps({
                "candidate_summary": "Error: API Key not found.",
                "match_score": 0,
                "key_skills": [],
                "missing_skills": [],
                "interview_questions": ["Please configure API Key in .env file."]
            })

        prompt = f"""
        You are an expert HR Recruitment AI. 
        Analyze the following resume against the Job Description.

        **Job Description:**
        {job_description}

        **Resume Context:**
        {resume_text}

        **Task:**
        1. Extract key skills from the resume.
        2. Calculate a relevance score (0-100%) based on the JD.
        3. Identify missing skills or gaps.
        4. Generate 3-5 specific interview questions to probe the candidate's fit.

        **Format Output as JSON:**
        {{
            "candidate_summary": "Brief summary...",
            "key_skills": ["Skill 1", "Skill 2"],
            "match_score": 85,
            "missing_skills": ["Skill A", "Skill B"],
            "seniority": "Estimated Level (e.g. Senior, Junior)",
            "interview_questions": [
                "Question 1",
                "Question 2"
            ]
        }}
        """
        
        try:
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return json.dumps({
                "candidate_summary": f"Error connecting to LLM: {str(e)}",
                "match_score": 0,
                "key_skills": [],
                "missing_skills": [],
                "interview_questions": []
            })

def get_analyzer(engine_type="Rule-Based"):
    """Factory method to get the analyzer instance."""
    if engine_type == "Gemini LLM":
        return GeminiAnalyzer()
    else:
        return KeywordAnalyzer()
