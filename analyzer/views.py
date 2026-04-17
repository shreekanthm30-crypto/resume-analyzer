from django.shortcuts import render
from .models import Resume, AnalysisResult
import fitz
import re
from openai import OpenAI
from django.conf import settings
import json
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from io import BytesIO

# Initialize OpenAI client only if API key is available
client = None
if settings.OPENAI_API_KEY:
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
    except Exception as e:
        print(f"Failed to initialize OpenAI client: {e}")
        client = None

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        text = ""
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def parse_resume_data(text):
    """Parse structured data from resume text using regex and basic NLP"""
    data = {
        'name': '',
        'email': '',
        'phone': '',
        'skills': [],
        'experience_years': None
    }

    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    if emails:
        data['email'] = emails[0]

    # Extract phone
    phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    phones = re.findall(phone_pattern, text)
    if phones:
        data['phone'] = phones[0]

    # Extract potential name (first line or capitalized words)
    lines = text.split('\n')[:5]  # Check first 5 lines
    for line in lines:
        line = line.strip()
        if line and len(line.split()) <= 4 and not '@' in line and not any(char.isdigit() for char in line):
            # Check if it looks like a name
            words = line.split()
            if all(word[0].isupper() for word in words if word):
                data['name'] = line
                break

    # Extract skills (common tech skills)
    common_skills = [
        'Python', 'Java', 'JavaScript', 'C++', 'C#', 'PHP', 'Ruby', 'Go', 'Rust',
        'React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask', 'Spring', 'Laravel',
        'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'AWS', 'Azure', 'GCP',
        'Docker', 'Kubernetes', 'Git', 'Linux', 'HTML', 'CSS', 'Bootstrap', 'jQuery',
        'Machine Learning', 'AI', 'Data Science', 'TensorFlow', 'PyTorch'
    ]

    found_skills = []
    text_lower = text.lower()
    for skill in common_skills:
        if skill.lower() in text_lower:
            found_skills.append(skill)

    data['skills'] = found_skills

    # Estimate experience years
    experience_patterns = [
        r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
        r'experience.*?(\d+)\+?\s*years?',
        r'(\d+)\+?\s*years?\s+in'
    ]

    for pattern in experience_patterns:
        matches = re.findall(pattern, text_lower)
        if matches:
            years = [int(match) for match in matches]
            data['experience_years'] = max(years)
            break

    return data

def analyze_resume_with_ai(text, job_description):
    """Enhanced AI analysis with better prompt engineering"""
    # Check if OpenAI client is available
    if not client:
        return analyze_resume_fallback(text, job_description)

    try:
        prompt = f"""
Analyze this resume against the job description. Provide a detailed analysis in JSON format.

Resume Text:
{text[:1000]}

Job Description:
{job_description[:500]}

Return a JSON object with these exact keys:
{{
    "match_score": <number 0-100>,
    "matched_skills": [<array of skills from resume that match job>],
    "missing_skills": [<array of skills mentioned in job but missing from resume>],
    "suggestions": "<string with improvement suggestions>",
    "strengths": [<array of resume strengths>],
    "weaknesses": [<array of resume weaknesses>]
}}

Be specific and accurate. Focus on technical skills, experience, and job requirements.
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.3
        )

        ai_response = response.choices[0].message.content.strip()

        # Try to parse JSON response
        try:
            # Clean the response if it has markdown formatting
            if ai_response.startswith('```json'):
                ai_response = ai_response[7:]
            if ai_response.endswith('```'):
                ai_response = ai_response[:-3]

            result = json.loads(ai_response.strip())

            return {
                'match_score': result.get('match_score', 50),
                'matched_skills': result.get('matched_skills', []),
                'missing_skills': result.get('missing_skills', []),
                'suggestions': result.get('suggestions', 'Analysis completed successfully.'),
                'strengths': result.get('strengths', []),
                'weaknesses': result.get('weaknesses', []),
                'ai_response': ai_response
            }

        except json.JSONDecodeError:
            # Fallback parsing if JSON fails
            return {
                'match_score': 60,
                'matched_skills': ["Communication", "Problem Solving"],
                'missing_skills': ["Advanced Technical Skills"],
                'suggestions': "Consider adding more specific technical skills relevant to the job.",
                'strengths': ["Good foundation"],
                'weaknesses': ["Limited technical details"],
                'ai_response': ai_response
            }

    except Exception as e:
        print(f"AI Analysis error: {e}")
        return {
            'match_score': 50,
            'matched_skills': ["Basic skills"],
            'missing_skills': ["Advanced skills"],
            'suggestions': "Analysis completed with limited AI capabilities.",
            'strengths': [],
            'weaknesses': [],
            'ai_response': str(e)
        }

def analyze_resume_fallback(text, job_description):
    """Fallback analysis when OpenAI API key is not available"""
    # Basic keyword matching analysis
    resume_lower = text.lower()
    job_lower = job_description.lower()

    # Common technical skills to check
    common_skills = [
        'python', 'java', 'javascript', 'html', 'css', 'sql', 'react', 'angular', 'vue',
        'django', 'flask', 'spring', 'node.js', 'express', 'mongodb', 'postgresql', 'mysql',
        'aws', 'docker', 'kubernetes', 'git', 'linux', 'agile', 'scrum', 'api', 'rest'
    ]

    matched_skills = []
    missing_skills = []

    for skill in common_skills:
        if skill in resume_lower and skill in job_lower:
            matched_skills.append(skill.title())
        elif skill in job_lower and skill not in resume_lower:
            missing_skills.append(skill.title())

    # Calculate basic match score based on skill matching
    if matched_skills:
        match_score = min(95, 40 + (len(matched_skills) * 10))
    else:
        match_score = 35

    # Basic suggestions
    suggestions = "This is a basic analysis without AI. For detailed analysis, please configure OpenAI API key in environment variables."

    if missing_skills:
        suggestions += f" Consider adding these skills: {', '.join(missing_skills[:3])}."

    strengths = ["Resume uploaded successfully"]
    if matched_skills:
        strengths.append(f"Found {len(matched_skills)} matching skills")

    weaknesses = []
    if missing_skills:
        weaknesses.append(f"Missing {len(missing_skills)} relevant skills")
    if len(text) < 500:
        weaknesses.append("Resume appears to be brief")

    return {
        'match_score': match_score,
        'matched_skills': matched_skills,
        'missing_skills': missing_skills[:5],  # Limit to 5
        'suggestions': suggestions,
        'strengths': strengths,
        'weaknesses': weaknesses,
        'ai_response': 'Basic analysis completed (OpenAI API key not configured)'
    }

def home(request):
    if request.method == "POST":
        file = request.FILES.get("resume")
        job_desc = request.POST.get("job_description", "")

        if not file:
            return render(request, "home.html", {"error": "Please upload a resume file."})
        if not job_desc.strip():
            return render(request, "home.html", {"error": "Please enter a job description."})

        # Validate file type
        if not file.name.lower().endswith('.pdf'):
            return render(request, "home.html", {"error": "Please upload a PDF file only."})

        # Validate file size (max 10MB)
        if file.size > 10 * 1024 * 1024:
            return render(request, "home.html", {"error": "File size must be less than 10MB."})

        try:
            # Create resume object
            resume_obj = Resume.objects.create(file=file)

            # Extract and parse text
            text = extract_text_from_pdf(resume_obj.file.path)

            if not text.strip():
                resume_obj.delete()  # Clean up
                return render(request, "home.html", {"error": "Could not read text from the PDF. Please ensure it contains readable text."})

            # Parse resume data
            parsed_data = parse_resume_data(text)

            # Update resume with parsed data
            resume_obj.extracted_text = text
            resume_obj.name = parsed_data['name']
            resume_obj.email = parsed_data['email']
            resume_obj.phone = parsed_data['phone']
            resume_obj.skills = parsed_data['skills']
            resume_obj.experience_years = parsed_data['experience_years']
            resume_obj.save()

            # Perform AI analysis
            analysis_result = analyze_resume_with_ai(text, job_desc)

            # Save analysis result
            analysis = AnalysisResult.objects.create(
                resume=resume_obj,
                job_description=job_desc,
                match_score=analysis_result['match_score'],
                matched_skills=analysis_result['matched_skills'],
                missing_skills=analysis_result['missing_skills'],
                suggestions=analysis_result['suggestions'],
                ai_response=analysis_result['ai_response']
            )

            # Prepare context for template
            context = {
                "score": analysis_result['match_score'],
                "matched": analysis_result['matched_skills'],
                "missing": analysis_result['missing_skills'],
                "suggestions": analysis_result['suggestions'],
                "strengths": analysis_result['strengths'],
                "weaknesses": analysis_result['weaknesses'],
                "resume_data": {
                    "name": parsed_data['name'],
                    "email": parsed_data['email'],
                    "phone": parsed_data['phone'],
                    "skills": parsed_data['skills'],
                    "experience_years": parsed_data['experience_years']
                },
                "analysis_id": analysis.id
            }

            return render(request, "home.html", context)

        except Exception as e:
            # Clean up any created objects on error
            if 'resume_obj' in locals():
                try:
                    resume_obj.delete()
                except:
                    pass
            return render(request, "home.html", {"error": f"An error occurred: {str(e)}"})
    
    return render(request, "home.html", {
        'openai_available': client is not None
    })

def download_analysis(request, analysis_id):
    """Generate and download a PDF report of the analysis"""
    analysis = get_object_or_404(AnalysisResult, id=analysis_id)

    # Create PDF buffer
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title = Paragraph("AI Resume Analysis Report", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))

    # Resume Info
    if analysis.resume.name:
        story.append(Paragraph(f"<b>Candidate:</b> {analysis.resume.name}", styles['Normal']))
    if analysis.resume.email:
        story.append(Paragraph(f"<b>Email:</b> {analysis.resume.email}", styles['Normal']))
    story.append(Paragraph(f"<b>Analysis Date:</b> {analysis.created_at.strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Match Score
    story.append(Paragraph(f"<b>Match Score: {analysis.match_score}%</b>", styles['Heading2']))
    story.append(Spacer(1, 6))

    # Matched Skills
    if analysis.matched_skills:
        story.append(Paragraph("<b>Matched Skills:</b>", styles['Heading3']))
        skills_text = ", ".join(analysis.matched_skills)
        story.append(Paragraph(skills_text, styles['Normal']))
        story.append(Spacer(1, 6))

    # Missing Skills
    if analysis.missing_skills:
        story.append(Paragraph("<b>Missing Skills:</b>", styles['Heading3']))
        skills_text = ", ".join(analysis.missing_skills)
        story.append(Paragraph(skills_text, styles['Normal']))
        story.append(Spacer(1, 6))

    # Suggestions
    if analysis.suggestions:
        story.append(Paragraph("<b>AI Suggestions:</b>", styles['Heading3']))
        story.append(Paragraph(analysis.suggestions, styles['Normal']))
        story.append(Spacer(1, 12))

    # Job Description Preview
    story.append(Paragraph("<b>Job Description Preview:</b>", styles['Heading3']))
    job_preview = analysis.job_description[:300] + "..." if len(analysis.job_description) > 300 else analysis.job_description
    story.append(Paragraph(job_preview, styles['Normal']))

    # Build PDF
    doc.build(story)

    # Return PDF response
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="resume_analysis_{analysis_id}.pdf"'
    return response

def analysis_history(request):
    """View analysis history"""
    analyses = AnalysisResult.objects.all().order_by('-created_at')[:20]  # Last 20 analyses

    context = {
        'analyses': analyses
    }

    return render(request, 'history.html', context)
