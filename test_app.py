import requests

# Test the resume analyzer
url = "http://127.0.0.1:8000/"
data = {
    "job_description": "Python developer with Django experience"
}

# Create a simple test PDF content (this won't be a real PDF but will test the error handling)
files = {
    "resume": ("test.pdf", b"Sample resume text content", "application/pdf")
}

try:
    response = requests.post(url, data=data, files=files, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")