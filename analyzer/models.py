from django.db import models
import json

class Resume(models.Model):
    file = models.FileField(upload_to='resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # Extracted data
    extracted_text = models.TextField(blank=True)
    name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    skills = models.JSONField(default=list, blank=True)
    experience_years = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.file.name

class AnalysisResult(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    job_description = models.TextField()
    match_score = models.IntegerField()
    matched_skills = models.JSONField(default=list)
    missing_skills = models.JSONField(default=list)
    suggestions = models.TextField()
    ai_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis for {self.resume.file.name} - Score: {self.match_score}%"

