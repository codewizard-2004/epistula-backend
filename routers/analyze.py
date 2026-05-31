from fastapi import APIRouter, HTTPException, Request
from models.analyze_models import AnalyzeRequest, AnalyzeResponse, MatchingRequest, MatchingResponse
from agents.analysis.chains import analysis_in_parallel, quick_analyze_match
from agents.extraction.chains import parse_job_description

router = APIRouter(
    prefix="/api/analyze",
    tags=["Analyze"]
)

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
    
    

    
