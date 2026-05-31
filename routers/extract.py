from agents.verify.chains import check_is_job_description, check_is_resume
from fastapi import APIRouter, HTTPException, File,Form, UploadFile, Request
from models.schema import Resume
from agents.extraction.chains import parsing_in_parallel, parse_resume
import io
from pypdf import PdfReader
from models.schema import ParseResponse    

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
        if check_is_job_description(request.app.state.google_llm, job_description) and check_is_resume(request.app.state.google_llm, resume_text):
            result = parsing_in_parallel(request.app.state.google_llm, job_description, resume_text)
        else:
            raise HTTPException(status_code=422, detail="Either the uploaded file is not a resume or the job description is not a valid job description")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing failed: {e}")
 
    return ParseResponse(
        parsed_jd=result["parsed_jd"],
        parsed_resume=result["parsed_resume"],
        raw_resume=result["raw_resume"],
    )

@router.post("/resume", response_model = Resume)
async def parse_resume_only(
    request: Request,
    resume_file: UploadFile = File(...)
):
    """
    Step 1 — Parse resume only.
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
        is_resume = check_is_resume(request.app.state.google_llm, resume_text)
        if is_resume:
            result = parse_resume(request.app.state.google_llm, resume_text)
        else:
            raise HTTPException(status_code=422, detail="The uploaded file is not a resume")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing failed: {e}")
 
    return result