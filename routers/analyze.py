"""
THIS FILE WILL CONTAIN FUNCTIONS TO
1) ANALYZE THE RESUME WITH JOB DESCRIPTION
2) ANALYZE THE RESUME'S ATS FRIENDLINESS
"""

from fastapi import APIRouter, HTTPException, File, UploadFile, Request
from models.schema import JobDescription, Resume, MatchingResponse, ATSResponse
#from services.chains import parse_jobdescription, parse_resume, analyze_match, check_ats
from services.chains import parsing_in_parallel, analysis_in_parallel
from pydantic import BaseModel
from services.chains import parse_job_description, quick_analyze_match

router = APIRouter(
    prefix="/api/analyze",
    tags=["Analyze"]
)

class AnalyzeRequest(BaseModel):
    parsed_jd: JobDescription
    parsed_resume: Resume
    raw_resume: str

class AnalyzeResponse(BaseModel):
    match_analysis: MatchingResponse
    ats_result: ATSResponse

@router.post("/", response_model=AnalyzeResponse)
async def analyze(body: AnalyzeRequest, request: Request):
    """
    Step 2 — Run match analysis + ATS check in parallel.
    Called after the user reviews / edits the parsed output and clicks Confirm.
    The request body is just the (possibly edited) ParseResponse + raw_resume.
    """
 
    try:
        result = analysis_in_parallel(
            llm = request.app.state.google_llm,
            job_desc=body.parsed_jd,
            resume=body.parsed_resume,
            raw_resume=body.raw_resume,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")
 
    return AnalyzeResponse(
        match_analysis=result["matching_analysis"],
        ats_result=result["ats_result"],
    )

class MatchingRequest(BaseModel):
    jd: str
    parsed_resume: Resume

class MatchingResponse(BaseModel):
    status: str
    matching_percentage: int

@router.post("/matching", response_model = MatchingResponse)
async def matching(body: MatchingRequest, request: Request):
    """
    1. This endpoint will take the pasred resume and job description as input
    2. Parse the job description
    3. Perform analysis and returns matching percentage
    """

    try:
        parsed_jd = parse_job_description(
            request.app.state.google_llm,
            body.jd
        )
        match_percentage = quick_analyze_match(
            request.app.state.google_llm,
            parsed_jd,
            body.parsed_resume
        )
        return MatchingResponse(
            status = "success",
            matching_percentage = match_percentage
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Matching analysis failed: {e}")
    
    

    
