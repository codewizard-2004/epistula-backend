"""
ALL PYDANTIC MODELS WILL BE STORED HERE
"""

from pydantic import BaseModel, Field
from typing import List, Optional

class JobDescription(BaseModel):
    title: str = Field(description="The title of the job", examples=["Software Engineer", "Data Scientist"])
    company: str = Field(description="The company offering the job", examples=["Google", "Microsoft"])
    location: str = Field(description="The location of the job", examples=["San Francisco, CA", "New York, NY"])
    education: str = Field(description="The education requirements for the job", examples=["Bachelor's degree in Computer Science", "Master's degree in Data Science"])
    experience: int = Field(description="The experience requirements for the job in years", examples=[3, 5, 7])
    employment_type: str = Field(description="The type of employment", examples=["Full-time", "Part-time", "Contract", "Internship"])
    required_skills: List[str] = Field(description="The requirements of the job", examples=["3+ years of experience in software development", "Proficiency in Python and JavaScript", "Fluent in German"])
    soft_skills: List[str] = Field(description="The soft skills required for the job", examples=["Good communication skills", "Ability to work in a team"])
    responsibilities: List[str] = Field(description="The responsibilities of the job", examples=["Develop and maintain software applications", "Collaborate with cross-functional teams"])
    salary_range: Optional[str] = Field(description="The salary range for the job", examples=["$80,000 - $120,000", "1,00,000Rs - $5,00,000Rs"])

class Resume(BaseModel):
    name: str = Field(description="The full name of the person", examples=["John Doe", "Jane Smith"])
    email: str = Field(description="The email address of the person", examples=["john.doe@example.com", "jane.smith@example.com"])
    phone: str = Field(description="The phone number of the person", examples=["123-456-7890", "987-654-3210"])
    education: List[str] = Field(description="The education details of the person", examples=["Bachelor's degree in Computer Science from XYZ University", "Master's degree in Data Science from ABC University"])
    location: str = Field(description="The location of the person", examples=["San Francisco, CA", "New York, NY"])
    experience: int = Field(description="The experience details of the person in years", examples=[3, 5, 7])
    skills: List[str] = Field(description="The skills of the person", examples=["Python, JavaScript, SQL", "Machine Learning, Data Analysis, Deep Learning"])
    soft_skills: List[str] = Field(description="The soft skills of the person", examples=["Good communication skills", "Ability to work in a team"])
    certifications: Optional[List[str]] = Field(description="The certifications of the person", examples=["AWS Certified Solutions Architect", "Certified Data Scientist"])
    languages: Optional[List[str]] = Field(description="The languages known by the person", examples=["English", "Spanish", "French"])

class MatchingResponse(BaseModel):
    score: int = Field(description="The score indicating how well the resume matches the job description", ge=0, le=100, examples=[85, 90, 95])
    matched_skills: List[str] = Field(description="The list of skills that matched between the resume and the job description", examples=["Python", "JavaScript", "Communication skills"])
    skill_gaps: List[str] = Field(description="The list of skills that are required by the job description but are missing in the resume", examples=["SQL", "Machine Learning", "Experience gaps", "Leadership experience"])
    suggestions: List[str] = Field(description="The list of suggestions to improve the resume to better match the job description", examples=["Add SQL to your skills section", "Highlight your experience with machine learning in your resume"])

class ATSResponse(BaseModel):
    score: int = Field(description="The score indicating how well the resume is optimized for ATS", ge=0, le=100, examples=[80, 85, 90])
    issues: List[str] = Field(description="The list of issues that are affecting the resume's ATS optimization", examples=["Missing keywords", "Unusual formatting", "Lack of section headers"])
    suggestions: List[str] = Field(description="The list of suggestions to improve the resume's ATS optimization", examples=["Add relevant keywords from the job description", "Use standard section headers like 'Experience' and 'Education'", "Avoid using tables and graphics in your resume"])

class ParallelParsingOutput(BaseModel):
    parsed_jd: JobDescription
    parsed_resume: Resume
    raw_resume: str

class ParseResponse(BaseModel):
    """Returned after parallel parsing — sent to the UI for user review."""
    parsed_jd: JobDescription
    parsed_resume: Resume
    raw_resume: str   

class SearchJobRequest(BaseModel):
    query: str
    country: str = "in"
    city: str | None = None
    employment_types: List[str] = ["FULLTIME"]
    min_salary: int = 0
    page: int = 1
    num_pages: int = 1