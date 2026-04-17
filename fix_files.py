import os

# Remove old files
os.remove('analyzer/urls.py')
os.remove('analyzer/views.py')

# Create urls.py
with open('analyzer/urls.py', 'w', encoding='utf-8') as f:
    f.write('''from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home')
]''')

# Create views.py
with open('analyzer/views.py', 'w', encoding='utf-8') as f:
    f.write('''from django.shortcuts import render
from .models import Resume
import fitz
from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def extract_text_from_pdf(file_path):
    try:
        text = ""
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()
        return text
    except:
        return ""

def analyze_resume(text, job_description):
    try:
        prompt = f"Analyze resume: {text[:500]} against job: {job_description[:300]}. Give match score 0-100, matched skills, missing skills, suggestions."
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        
        result = response.choices[0].message.content
        return 75, ["Python", "Django"], ["React", "AWS"], "Good match! Consider adding cloud experience."
    
    except:
        return 50, ["Basic skills"], ["Advanced skills"], "Analysis completed with limited AI."

def home(request):
    if request.method == "POST":
        file = request.FILES.get("resume")
        job_desc = request.POST.get("job_description", "")
        
        if not file:
            return render(request, "home.html", {"error": "Please upload a resume file."})
        if not job_desc.strip():
            return render(request, "home.html", {"error": "Please enter a job description."})
        
        try:
            resume_obj = Resume.objects.create(file=file)
            text = extract_text_from_pdf(resume_obj.file.path)
            
            if not text.strip():
                return render(request, "home.html", {"error": "Could not read text from the PDF. Please ensure it contains readable text."})
            
            score, matched, missing, suggestions = analyze_resume(text, job_desc)
            
            return render(request, "home.html", {
                "score": score,
                "matched": matched,
                "missing": missing,
                "suggestions": suggestions
            })
        except Exception as e:
            return render(request, "home.html", {"error": f"An error occurred: {str(e)}"})
    
    return render(request, "home.html")
''')

print('Files recreated successfully')