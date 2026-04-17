import fitz  # PyMuPDF
from openai import OpenAI
import os
from typing import List
from django.conf import settings

# Initialize OpenAI client
client = OpenAI(api_key=getattr(settings, 'OPENAI_API_KEY', os.getenv('OPENAI_API_KEY', 'your-api-key-here')))

def extract_text_from_pdf(file_path):
    try:
        text = ""
        doc = fitz.open(file_path)

        for page in doc:
            text += page.get_text()

        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def extract_skills_with_ai(text: str) -> List[str]:
    """Extract skills from resume text using AI"""
    prompt = f"""
    Extract all technical skills, programming languages, frameworks, tools, and technologies mentioned in the following resume text.
    Return only a comma-separated list of skills, nothing else. If no skills are found, return an empty string.

    Resume text:
    {text[:2000]}  # Limit text to avoid token limits
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.1
        )
        skills_text = response.choices[0].message.content.strip()
        if skills_text:
            skills = [skill.strip().lower() for skill in skills_text.split(',') if skill.strip()]
            return list(set(skills))  # Remove duplicates
        return []
    except Exception as e:
        print(f"Error extracting skills with AI: {e}")
        # Fallback: simple keyword matching
        fallback_skills = ['python', 'java', 'c++', 'django', 'html', 'css', 'javascript', 'sql', 'react', 'node', 'git']
        found = [skill for skill in fallback_skills if skill in text.lower()]
        return found

def extract_job_skills_with_ai(job_description: str) -> List[str]:
    """Extract required skills from job description using AI"""
    prompt = f"""
    Extract all required technical skills, programming languages, frameworks, tools, and technologies from the following job description.
    Focus on skills that are explicitly mentioned as required or preferred.
    Return only a comma-separated list of skills, nothing else. If no skills are found, return an empty string.

    Job Description:
    {job_description[:2000]}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.1
        )
        skills_text = response.choices[0].message.content.strip()
        if skills_text:
            skills = [skill.strip().lower() for skill in skills_text.split(',') if skill.strip()]
            return list(set(skills))
        return []
    except Exception as e:
        print(f"Error extracting job skills with AI: {e}")
        # Fallback: simple keyword matching
        fallback_skills = ['python', 'django', 'sql', 'api', 'html', 'css', 'javascript', 'react']
        found = [skill for skill in fallback_skills if skill in job_description.lower()]
        return found

def generate_suggestions(resume_skills: List[str], job_skills: List[str], matched: List[str], missing: List[str]) -> str:
    """Generate AI-powered suggestions for improving the resume"""
    prompt = f"""
    Based on the following analysis, provide 2-3 specific, actionable suggestions to improve the resume match for this job.
    Be encouraging and constructive.

    Resume skills: {', '.join(resume_skills)}
    Required job skills: {', '.join(job_skills)}
    Matched skills: {', '.join(matched)}
    Missing skills: {', '.join(missing)}

    Provide suggestions in a friendly paragraph format.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating suggestions: {e}")
        # Fallback suggestions
        if missing:
            return f"To improve your resume, consider adding experience with: {', '.join(missing[:3])}. You could take online courses or work on personal projects to gain these skills."
        else:
            return "Great job! Your resume already matches most of the required skills. Consider highlighting your experience with these skills more prominently in your resume."

def calculate_score(resume_skills, job_skills):
    matched = set(resume_skills) & set(job_skills)
    missing = set(job_skills) - set(resume_skills)

    if len(job_skills) == 0:
        return 0, [], []

    score = (len(matched) / len(job_skills)) * 100

    return round(score, 2), list(matched), list(missing)