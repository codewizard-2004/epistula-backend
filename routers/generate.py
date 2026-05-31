from fastapi import APIRouter, HTTPException, Request
from services.chains import generate_cover_letter, generate_cover_email
from models.generate_models import GenerateRequest, GenerateResponse, GenerateRequestV1

router = APIRouter(
    prefix="/api",
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

@router.post("/v1/generate", response_model = GenerateResponse)
async def generate_v1(body: GenerateRequestV1, request: Request):
    """
    This endpoint is used to directly perform cover letter generation directly without performing analysis.
    It works by parsing the job description and resume and straight to generation
    
    Args:
        body (GenerateRequestV1): The request body containing the parsed job description, parsed resume and tone.
        request (Request): The request object.
    Returns:
        GenerateResponse: A JSON object containing the generated cover letter and cover email.
    """
    try:
        cover_letter = generate_cover_letter(
            request.app.state.google_llm,
            job_desc=body.parsed_jd,
            resume=body.parsed_resume,
            match_response = None,
            tone=body.tone,
        )
 
        cover_email = None
        if body.generate_email:
            cover_email = generate_cover_email(
                request.app.state.google_llm,
                job_desc=body.parsed_jd,
                resume=body.parsed_resume,
                match_response = None,
            )
 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {e}")
 
    return GenerateResponse(cover_letter=cover_letter, cover_email=cover_email)

    
    
