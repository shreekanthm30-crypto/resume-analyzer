# AI Resume Analyzer

A Django-based web application that uses AI to analyze resumes against job descriptions and provide match scores, matched/missing skills, and personalized suggestions.

## Features

- Upload PDF resumes
- AI-powered skill extraction from resumes (with fallback to keyword matching)
- AI-powered skill extraction from job descriptions (with fallback)
- Match score calculation
- Personalized improvement suggestions (with fallback)
- Modern, responsive UI with Bootstrap

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Set up your OpenAI API key:
   - Get an API key from [OpenAI](https://platform.openai.com/api-keys)
   - Add it to `config/settings.py`:
     ```python
     OPENAI_API_KEY = 'your-actual-api-key-here'
     ```
   - Or set as environment variable: `OPENAI_API_KEY=your-key`
   - **Note**: If the API key has insufficient quota, the app will use fallback keyword-based extraction.

6. Run migrations:
   ```bash
   python manage.py migrate
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

8. Open http://127.0.0.1:8000/ in your browser

## How It Works

1. **Resume Upload**: Users upload their PDF resume
2. **Job Description Input**: Users paste the job description
3. **AI Analysis**:
   - GPT-3.5-turbo extracts skills from the resume
   - GPT-3.5-turbo extracts required skills from the job description
   - Calculates match percentage
   - Generates personalized suggestions
4. **Results Display**: Shows score, matched skills, missing skills, and suggestions

## Dependencies

- Django
- PyMuPDF (for PDF text extraction)
- OpenAI (for AI analysis)
- Bootstrap (for UI)

## API Usage

The app uses OpenAI's GPT-3.5-turbo model for:
- Skill extraction (max 200 tokens per call)
- Suggestion generation (max 300 tokens)

Monitor your OpenAI usage to avoid unexpected costs.

## Security Notes

- This is a development setup
- In production, use proper file validation and storage
- Secure your API keys
- Consider rate limiting for API calls