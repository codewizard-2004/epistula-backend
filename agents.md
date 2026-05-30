# Epistula Backend Agent Documentation

This document provides a comprehensive guide to the Epistula backend architecture, designed specifically to help AI agents (and human developers) understand the project's structure, API endpoints, data schemas, and Langchain-based AI services.

## 📁 Directory Structure

The backend is built with FastAPI and organized into several key directories:

- `main.py`: The entry point for the FastAPI application. Configures CORS, lifecycle events (LLM initialization), and includes routers.
- `models/`: Contains all data schemas, primarily using Pydantic.
  - `schema.py`: Defines the core domain models used throughout the application.
- `routers/`: Contains the FastAPI route definitions, organized by functionality.
  - `extract.py`: Endpoints for parsing Resumes and Job Descriptions.
  - `analyze.py`: Endpoints for matching analysis and ATS scoring.
  - `generate.py`: Endpoints for generating cover letters and emails.
  - `jobs.py`: Placeholder for job search integration.
- `services/`: Contains the core business logic and AI agents.
  - `chains.py`: Defines the Langchain agents and parallel execution pipelines.
  - `prompts.py`: Stores the system prompts used by the Langchain agents.

## 🔄 Core Architecture Flow

The system uses a sequential, multi-step pipeline where each step is handled by specific AI agents:

1. **Parse (`/api/parse/`)**: Extract structured data from raw Resume PDFs and Job Description text.
2. **Analyze (`/api/analyze/`)**: Compare the parsed Resume against the parsed Job Description to calculate match scores and ATS readiness.
3. **Generate (`/api/generate` and `/api/v1/generate`)**: Create tailored artifacts (Cover Letters and Emails) using the parsed data, and optionally analysis results.

## 🔌 API Endpoints

### 1. Parsing Router (`/api/parse/`)
Extracts structured information from a user's resume and a given job description. Uses parallel execution to reduce latency.

- **Method**: `POST`
- **Inputs**:
  - `resume_file`: UploadFile (PDF only)
  - `job_description`: Form field (string)
- **Response Model**: `ParseResponse`
  - `parsed_jd`: `JobDescription`
  - `parsed_resume`: `Resume`
  - `raw_resume`: string (extracted text from PDF)

**Example Request (Multipart/form-data)**
- `resume_file`: `(Binary PDF File)`
- `job_description`: `"We are looking for a Python developer with 3 years of experience..."`

**Example Response (JSON)**
```json
{
  "parsed_jd": {
    "title": "Python Developer",
    "company": "Tech Corp",
    "location": "Remote",
    "education": "Bachelor's",
    "experience": 3,
    "employment_type": "Full-time",
    "required_skills": ["Python", "FastAPI"],
    "soft_skills": ["Communication"],
    "responsibilities": ["Develop APIs"],
    "salary_range": "$100k - $120k"
  },
  "parsed_resume": {
    "name": "Jane Doe",
    "email": "jane@example.com",
    "phone": "555-0100",
    "location": "New York",
    "education": ["B.S. Computer Science"],
    "experience": 4,
    "skills": ["Python", "Django", "FastAPI"],
    "soft_skills": ["Teamwork"],
    "certifications": [],
    "languages": ["English"]
  },
  "raw_resume": "Jane Doe... (full text)"
}
```

### 2. Analysis Router (`/api/analyze/`)
Analyzes the match between the resume and job description, and checks ATS friendliness.

- **Method**: `POST`
- **Request Model**: `AnalyzeRequest`
  - Requires the `parsed_jd` (JobDescription), `parsed_resume` (Resume), and `raw_resume` (string) (typically passed directly from the Parse step after user review).
- **Response Model**: `AnalyzeResponse`
  - `match_analysis`: `MatchingResponse`
  - `ats_result`: `ATSResponse`

**Example Request (JSON)**
```json
{
  "parsed_jd": { /* JobDescription Object */ },
  "parsed_resume": { /* Resume Object */ },
  "raw_resume": "Jane Doe... (full text)"
}
```

**Example Response (JSON)**
```json
{
  "match_analysis": {
    "score": 85,
    "matched_skills": ["Python", "FastAPI"],
    "skill_gaps": ["Cloud Architecture"],
    "suggestions": ["Add more details about cloud deployments."]
  },
  "ats_result": {
    "score": 90,
    "issues": ["Missing keywords: Cloud Architecture"],
    "suggestions": ["Include exact keyword 'Cloud Architecture' under skills."]
  }
}
```

### 3. Generation Router (`/api/generate` and `/api/v1/generate`)
Generates tailored cover letters and emails based on the parsed data and optionally the analysis.

#### Endpoint: `/api/generate`
Uses the match analysis results to generate highly tailored artifacts.

- **Method**: `POST`
- **Request Model**: `GenerateRequest`
  - Requires `parsed_jd` (JobDescription), `parsed_resume` (Resume), `matching_analysis` (MatchingResponse).
  - Optional: `tone` (string, default "Professional"), and `generate_email` (boolean, default False).
- **Response Model**: `GenerateResponse`

**Example Request (JSON)**
```json
{
  "parsed_jd": { /* JobDescription Object */ },
  "parsed_resume": { /* Resume Object */ },
  "matching_analysis": { /* MatchingResponse Object */ },
  "tone": "Professional",
  "generate_email": true
}
```

#### Endpoint: `/api/v1/generate` (Direct Generation)
Generates the cover letter directly from the parsed Job Description and Resume, bypassing the match analysis step.

- **Method**: `POST`
- **Request Model**: `GenerateRequestV1`
  - Requires `parsed_jd` (JobDescription), `parsed_resume` (Resume).
  - Optional: `tone` (string, default "Professional"), and `generate_email` (boolean, default False).
- **Response Model**: `GenerateResponse`

**Example Request (JSON)**
```json
{
  "parsed_jd": { /* JobDescription Object */ },
  "parsed_resume": { /* Resume Object */ },
  "tone": "Professional",
  "generate_email": true
}
```

**Example Response (JSON) (For both endpoints)**
```json
{
  "cover_letter": "Dear Hiring Manager,\n\nI am writing to express my interest in the Python Developer position...",
  "cover_email": "Subject: Application for Python Developer - Jane Doe\n\nHi,\n\nPlease find my resume attached..."
}
```

## 🧠 Langchain Agents & Chains (`services/chains.py`)

The application leverages several specialized agents, utilizing `ChatGoogleGenerativeAI` and `langchain.agents.create_agent`:

- `parse_job_description`: Parses raw text into a `JobDescription` object.
- `parse_resume`: Parses raw resume text into a `Resume` object.
- `analyze_match`: Compares `JobDescription` and `Resume` to output a `MatchingResponse`.
- `check_ats`: Evaluates raw resume text for ATS optimization, returning an `ATSResponse`.
- `generate_cover_letter`: Uses JD, Resume, and Match Analysis to draft a tailored cover letter.
- `generate_cover_email`: Uses JD, Resume, and Match Analysis to draft a tailored email.

### Parallel Processing Pipelines
To optimize performance, certain agents are grouped into parallel runnables using `RunnableParallel`:
- `parsing_in_parallel`: Runs JD parsing and Resume parsing concurrently.
- `analysis_in_parallel`: Runs Match Analysis and ATS Checking concurrently.

## 📊 Data Schemas (`models/schema.py`)

Here are the primary Pydantic models used for input validation and structured LLM outputs:

### Domain Models

**`JobDescription`**
- `title` (str): Job title.
- `company` (str): Company name.
- `location` (str): Job location.
- `education` (str): Education requirements.
- `experience` (int): Required years of experience.
- `employment_type` (str): E.g., Full-time, Contract.
- `required_skills` (List[str]): Hard skills required.
- `soft_skills` (List[str]): Soft skills required.
- `responsibilities` (List[str]): Key duties.
- `salary_range` (Optional[str]): Compensation.

**`Resume`**
- `name` (str), `email` (str), `phone` (str), `location` (str).
- `education` (List[str]): Educational background.
- `experience` (int): Years of experience.
- `skills` (List[str]), `soft_skills` (List[str]).
- `certifications` (Optional[List[str]]), `languages` (Optional[List[str]]).

**`MatchingResponse`**
- `score` (int): 0-100 match score.
- `matched_skills` (List[str]): Skills present in both JD and Resume.
- `skill_gaps` (List[str]): Skills required but missing.
- `suggestions` (List[str]): Actionable advice to improve match.

**`ATSResponse`**
- `score` (int): 0-100 ATS optimization score.
- `issues` (List[str]): Identified ATS parsing problems.
- `suggestions` (List[str]): Advice to improve ATS formatting.
