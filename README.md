# Epistula AI Backend

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-1.0-orange)](https://github.com/langchain-ai/langchain)
[![Gemini](https://img.shields.io/badge/Google-Gemini-red?logo=googlegemini)](https://deepmind.google/technologies/gemini/)

**Epistula AI** is an intelligent, agentic resume parsing and scoring backend. It parses resume PDFs and Job Descriptions in parallel, evaluates ATS scoring and suitability matching, and automatically generates highly targeted cover letters and application emails.

---

## 🚀 Features

- **Parallel Parsing**: Uses LangChain runnables to parse a PDF resume and job description text concurrently.
- **ATS Compatibility Scoring**: Analyzes structural issues, missing keywords, and layout friendliness for Applicant Tracking Systems.
- **Suitability Matching**: Compares the parsed resume directly with the JD, computing a match percentage, finding skill gaps, and generating recommendations.
- **Tailored Assets**: Automatically writes a cover letter and a custom introductory email matching the desired tone.
- **Robust Security**: Features JWT-based per-user rate limiting (supporting both `HS256` and asymmetric `ES256` signing) to protect expensive LLM endpoints.

---

## 🛠️ Tech Stack & Dependencies

- **Framework**: FastAPI (Asynchronous Python Web framework)
- **AI Orchestration**: LangChain, `langchain-google-genai`
- **Models**: Google Gemini (`gemini-3.5-flash` by default), OpenRouter GPT models
- **PDF Extraction**: `pypdf`, `pymupdf4llm`
- **Configuration & Validation**: Pydantic v2, `pydantic-settings`
- **Security & Limiting**: `slowapi`, `PyJWT`, `cryptography`
- **Dependency Manager**: `uv`

---

## 📦 Getting Started

### 1. Prerequisites
- Python 3.12+ (Recommended 3.12 or 3.13; Pydantic warnings may show on Python 3.14+)
- A Google AI Studio API key (for Gemini) or OpenRouter API key

### 2. Environment Configuration
Create a `.env` file in the root directory (based on `example.env`):
```env
GOOGLE_API_KEY=AIzaSyC...your_gemini_key
OPENROUTER_API_KEY=sk-or-v1-...your_openrouter_key
GEMINI_MODEL=gemini-1.5-flash # Optional, defaults to gemini-1.5-flash
```

### 3. Installation
Using `uv` (recommended):
```bash
# Sync virtual environment and install dependencies
uv sync
```
Using standard `pip`:
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate # On Windows use: .venv\Scripts\activate

# Install dependencies
pip install .
```

---

## 💻 Running the Server

Start the FastAPI application using Uvicorn:

```bash
# Using uv
uv run uvicorn main:app --reload

# Using standard virtual environment
uvicorn main:app --reload
```

Once running, the backend server will be available at **`http://localhost:8000`**.

- **Interactive API Documentation (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative Documentation (Redoc)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🛡️ Security & Rate Limiting

The backend implements robust, per-user rate limiting using `slowapi` and Supabase JWT authentication.

- **Smart Rate Limiting**: Rate limits are applied based on the unique user ID (`sub` claim) extracted from the JWT Bearer token, gracefully falling back to the IP address for unauthenticated requests.
- **Differentiated Limits**:
  - `5/minute`: Applied to heavy AI/LLM endpoints (Analyze, Extract, Generate) to prevent abuse and manage API costs.
  - `10/minute`: Applied to standard data-fetching endpoints like Job Search.
- **Dynamic JWT Verification**: The authentication middleware automatically detects the JWT signing algorithm from the request header:
  - Supports standard `HS256` symmetric secrets.
  - Dynamically fetches the JSON Web Key Set (JWKS) from Supabase to verify modern asymmetric `ES256` signatures securely and seamlessly!

---

## 🔌 API Reference & Workflow

The API utilizes a 3-step sequential workflow to parse, analyze, and generate results.

### Step 1: Parse Resume & JD
Extracts structured JSON data from a raw PDF resume and job description text.

* **Endpoint**: `POST /api/parse/`
* **Content-Type**: `multipart/form-data`
* **Parameters**:
  - `resume_file` (File, PDF)
  - `job_description` (Text, raw description)
* **Example Curl**:
  ```bash
  curl -X POST "http://localhost:8000/api/parse/" \
    -F "resume_file=@/path/to/resume.pdf" \
    -F "job_description=We are looking for a Python Developer..."
  ```

---

### Step 2: Analyze Match & ATS Compatibility

#### Comprehensive Analysis
Computes match score, identifies keyword/skill gaps, and scores ATS optimization.

* **Endpoint**: `POST /api/analyze/`
* **Content-Type**: `application/json`
* **Request Payload**:
  ```json
  {
    "parsed_jd": {
      "title": "Software Engineer",
      "company": "NexaWave",
      "location": "Kochi, India",
      "education": "B.Tech in CS",
      "experience": 2,
      "employment_type": "Full-Time",
      "required_skills": ["Python", "FastAPI", "React Native"],
      "soft_skills": ["Problem Solving", "Communication"],
      "responsibilities": ["Build APIs", "Collaborate on UI"],
      "salary_range": "Competitive"
    },
    "parsed_resume": {
      "name": "Amal Varghese",
      "email": "amal@example.com",
      "phone": "+91 9999999999",
      "education": ["B.Tech CS, MEC Kochi"],
      "location": "Kochi, India",
      "experience": 0,
      "skills": ["Python", "FastAPI", "React"],
      "soft_skills": ["Communication", "Problem Solving"],
      "certifications": ["NPTEL Python"],
      "languages": ["English"]
    },
    "raw_resume": "Amal Varghese... Python... FastAPI..."
  }
  ```
* **Example Response**:
  ```json
  {
    "match_analysis": {
      "score": 80,
      "matched_skills": ["Python", "FastAPI"],
      "skill_gaps": ["React Native"],
      "suggestions": ["Add React Native experience to your projects if you have it."]
    },
    "ats_result": {
      "score": 85,
      "issues": ["Missing key term: React Native"],
      "suggestions": ["Incorporate more key tools from the JD description."]
    }
  }
  ```

#### Quick Matching
Returns just the match percentage between a raw Job Description and a parsed Resume.

* **Endpoint**: `POST /api/analyze/matching`
* **Content-Type**: `application/json`
* **Request Payload**:
  ```json
  {
    "jd": "Software Engineer role...",
    "parsed_resume": { 
      "name": "Amal Varghese",
      "email": "amal@example.com",
      "experience": 2,
      "skills": ["Python", "FastAPI"]
    }
  }
  ```
* **Example Response**:
  ```json
  {
    "status": "success",
    "matching_percentage": 85
  }
  ```

---

### Step 3: Generate Cover Letter & Email (Optional)
Generates a targeted cover letter and application email based on the match results.

* **Endpoint**: `POST /api/generate`
* **Content-Type**: `application/json`
* **Request Payload**:
  ```json
  {
    "parsed_jd": { ... },
    "parsed_resume": { ... },
    "matching_analysis": {
      "score": 80,
      "matched_skills": ["Python", "FastAPI"],
      "skill_gaps": ["React Native"],
      "suggestions": [...]
    },
    "tone": "Professional",
    "generate_email": true
  }
  ```
* **Example Response**:
  ```json
  {
    "cover_letter": "Dear Hiring Team at NexaWave,\n\nI am writing to express my strong interest in...",
    "cover_email": "Subject: Job Application: Amal Varghese\n\nDear Team..."
  }
  ```

---

### Step 4: Search Jobs
Searches for relevant jobs by parsing a natural language prompt using an LLM to extract parameters, then querying the Rapid API JSearch integration.

* **Endpoint**: `POST /api/jobs/search`
* **Content-Type**: `application/json`
* **Request Payload**:
  ```json
  {
    "prompt": "I want an IT job at Bangalore with a minimum salary of 50000 in India",
    "page": 1,
    "num_pages": 1
  }
  ```
* **Example Response**: Returns a JSON object with the matching job listings from the API.

---

## 🚦 Postman Testing Guide

To test the JSON endpoints (`/api/analyze/` and `/api/generate/generate`) in Postman:
1. Select the **Body** tab.
2. Select the **raw** radio button.
3. Click the dropdown on the far right (defaults to *Text*) and choose **JSON**. 
   - *This configures the request to send the necessary `Content-Type: application/json` header, avoiding `model_attributes_type` validation errors.*
4. Paste your JSON request payload and hit **Send**.

---

## 📝 License
This project is licensed under the MIT License.
