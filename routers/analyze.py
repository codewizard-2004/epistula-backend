"""
THIS FILE WILL CONTAIN FUNCTIONS TO
1) ANALYZE THE RESUME WITH JOB DESCRIPTION
2) ANALYZE THE RESUME'S ATS FRIENDLINESS
"""

from fastapi import APIRouter, HTTPException, File, UploadFile
from models.schema import JobDescription, Resume, MatchingResponse, ATSResponse
#from services.chains import parse_jobdescription, parse_resume, analyze_match, check_ats
from services.chains import run_generation_pipeline

router = APIRouter(
    prefix="/analyze",
    tags=["Analyze"]
)

# This endpoint will take the resume and job description as input in json format and will return the result of matching and ats check
@router.post("/", response_model=MatchingResponse)
async def analyze_matching(job_description: str, resume: UploadFile = File(...)):
    """
    1) This endpoint will take the resume as file and job description as string
    2) converts the resume file to text
    3) runs the generation pipeline to get matching response and ats response
    """
    pass