### THIS FILE WILL CONTAIN FUNCTIONS TO 
### 1) PARSE THE RESUME
### 2) PARSE THE JOB DESCRIPTION
### 3) PARSE THE JOB PROMPT


from fastapi import APIRouter, HTTPException, File,Form, UploadFile, Request
from models.schema import JobDescription, Resume, MatchingResponse, ATSResponse
#from services.chains import parse_jobdescription, parse_resume, analyze_match, check_ats
from services.chains import parsing_in_parallel
from pydantic import BaseModel
import io
from pypdf import PdfReader

class ParseResponse(BaseModel):
    """Returned after parallel parsing — sent to the UI for user review."""
    parsed_jd: JobDescription
    parsed_resume: Resume
    raw_resume: str       

router = APIRouter(prefix="/api/parse", tags=["Resume Parser"])

@router.post("/", response_model=ParseResponse)
async def parse(
    request: Request,
    resume_file: UploadFile = File(...),          # PDF or .txt upload
    job_description: str = Form(...),             # raw JD text from a textarea
):
    """
    Step 1 — Parse resume + JD in parallel.
    Returns structured data for the user to review / edit before analysis.
    """
    try:
        raw_bytes = await resume_file.read()
        # Only accept PDFs
        if not (
            (resume_file.content_type == "application/pdf")
            or resume_file.filename.lower().endswith(".pdf") # type: ignore
        ):
            raise HTTPException(status_code=415, detail="Only PDF files are accepted")

        try:
            reader = PdfReader(io.BytesIO(raw_bytes))
            resume_text = "".join((page.extract_text() or "") for page in reader.pages)
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Could not extract text from PDF: {e}")
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not read resume file: {e}")
 
    try:
        result = parsing_in_parallel(request.app.state.google_llm, job_description, resume_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing failed: {e}")
 
    return ParseResponse(
        parsed_jd=result["parsed_jd"],
        parsed_resume=result["parsed_resume"],
        raw_resume=result["raw_resume"],
    )