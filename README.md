# AI Resume Analyzer

A Django-based web application that uses AI to analyze resumes against job descriptions and provide match scores, matched/missing skills, and personalized suggestions.

## Features

- 📄 Upload PDF resumes
- 🤖 AI-powered skill extraction and analysis (with OpenAI GPT)
- 📊 Match score calculation (0-100)
- 💡 Personalized improvement suggestions
- 🎨 Modern, responsive UI with animations
- 🔄 Fallback keyword-based analysis when AI is unavailable
- 📱 Mobile-friendly design

## Local Development Setup

### Prerequisites
- Python 3.8+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/resume-analyzer.git
   cd resume-analyzer
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**
   ```bash
   # Copy the example file
   cp .env.example .env

   # Edit .env and add your OpenAI API key
   OPENAI_API_KEY=sk-proj-your-actual-api-key-here
   ```

6. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Open in browser**
   - Visit: http://127.0.0.1:8000/

## 🚀 Deploy to Render

### Step 1: Prepare Your Repository
Your repository is already configured for Render deployment with:
- `render.yaml` - Render service configuration
- `runtime.txt` - Python version specification
- Updated `settings.py` for production

### Step 2: Get OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key (starts with `sk-proj-`)

### Step 3: Deploy on Render

#### Option A: Using Render Dashboard (Recommended)

1. **Sign up/Login to Render**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

2. **Create New Web Service**
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Select the `resume-analyzer` repository

3. **Configure Build Settings**
   - **Name**: `resume-analyzer` (or your preferred name)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - **Start Command**: `python manage.py runserver 0.0.0.0:$PORT`

4. **Add Environment Variables**
   ```
   DEBUG=False
   SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
   OPENAI_API_KEY=sk-proj-your-actual-openai-key-here
   DJANGO_SETTINGS_MODULE=config.settings
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy your app
   - Your live URL will be: `https://your-app-name.onrender.com`

#### Option B: Using render.yaml (Blueprint)

1. **Push render.yaml to GitHub**
   ```bash
   git add render.yaml
   git commit -m "Add Render deployment configuration"
   git push origin main
   ```

2. **Create from Blueprint**
   - In Render dashboard, click "New" → "Blueprint"
   - Connect your repository
   - Render will read `render.yaml` and set up automatically

### Step 4: Database Setup
After deployment, run migrations in Render:
1. Go to your service in Render dashboard
2. Open "Shell" tab
3. Run: `python manage.py migrate`

### Step 5: Test Your Deployment
- Visit your Render URL
- Upload a resume PDF
- Test the analysis functionality

## 🔧 Configuration

### Environment Variables
- `DEBUG`: Set to `False` for production
- `SECRET_KEY`: Django secret key (auto-generated on Render)
- `OPENAI_API_KEY`: Your OpenAI API key for AI analysis
- `DJANGO_SETTINGS_MODULE`: `config.settings`

### Without OpenAI API Key
The app works without an API key using basic keyword matching:
- Shows matched/missing skills
- Provides basic suggestions
- Displays clear warning about limited functionality

## 📁 Project Structure

```
resume-analyzer/
├── analyzer/                 # Main Django app
│   ├── models.py            # Database models
│   ├── views.py             # View logic
│   ├── templates/           # HTML templates
│   └── utils.py             # Helper functions
├── config/                  # Django project settings
├── media/                   # Uploaded files
├── staticfiles/             # Collected static files
├── requirements.txt         # Python dependencies
├── render.yaml             # Render deployment config
├── runtime.txt             # Python version for Render
└── .env.example            # Environment variables template
```

## 🛠️ Technologies Used

- **Backend**: Django 4.2+
- **AI**: OpenAI GPT-3.5-turbo
- **PDF Processing**: PyMuPDF (Fitz)
- **Frontend**: Bootstrap 5, Custom CSS with animations
- **Database**: SQLite (development) / PostgreSQL (production)
- **Deployment**: Render

## 📝 API Usage

The app uses OpenAI's GPT-3.5-turbo for:
- Resume text analysis
- Skill extraction
- Job description parsing
- Personalized suggestions

**Cost**: ~$0.002 per analysis (very low cost)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## 📄 License

This project is open source. Feel free to use and modify.

## 🆘 Troubleshooting

### Common Issues:

1. **"OpenAI API key not configured"**
   - Add `OPENAI_API_KEY` environment variable
   - The app will still work with basic analysis

2. **"PDF reading failed"**
   - Ensure PDF contains selectable text (not just images)
   - Try a different PDF

3. **"Static files not loading"**
   - Run: `python manage.py collectstatic`
   - Check `STATIC_ROOT` in settings

4. **Database errors**
   - Run: `python manage.py migrate`
   - Check database file permissions

### Support
- Check the [Issues](https://github.com/yourusername/resume-analyzer/issues) page
- Create a new issue for bugs or feature requests

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