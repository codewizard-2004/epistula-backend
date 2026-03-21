"""
THIS FILE WILL CONTAIN FUNCTIONS TO
1) GENERATE COVER LETTER AND EMAIL

"""

from fastapi import APIRouter, HTTPException, File, UploadFile, Request
from models.schema import JobDescription, Resume, MatchingResponse, ATSResponse
#from services.chains import parse_jobdescription, parse_resume, analyze_match, check_ats
from services.chains import generate_cover_letter, generate_cover_email
from pydantic import BaseModel

class GenerateRequest(BaseModel):
    parsed_jd: JobDescription
    parsed_resume: Resume
    matching_analysis: MatchingResponse
    tone: str = "Professional"
    generate_email: bool = False
 
 
class GenerateResponse(BaseModel):
    cover_letter: str
    cover_email: str | None = None

router = APIRouter(
    prefix="/api/generate",
    tags=["Generate"]
)

@router.post("/generate", response_model=GenerateResponse)
async def generate(body: GenerateRequest, request: Request):
    """
    Step 3 (optional) — Generate cover letter and/or cover email.
    Called after analysis results are shown to the user.
    """
 
    try:
        cover_letter = generate_cover_letter(
            request.app.state.google_llm,
            job_desc=body.parsed_jd,
            resume=body.parsed_resume,
            match_response=body.matching_analysis,
            tone=body.tone,
        )
 
        cover_email = None
        if body.generate_email:
            cover_email = generate_cover_email(
                request.app.state.google_llm,
                job_desc=body.parsed_jd,
                resume=body.parsed_resume,
                match_response=body.matching_analysis,
            )
 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {e}")
 
    return GenerateResponse(cover_letter=cover_letter, cover_email=cover_email)
