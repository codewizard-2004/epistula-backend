from pydantic import BaseModel
from .schema import JobDescription, Resume
from .analyze_models import MatchingResponse

class GenerateRequest(BaseModel):
    parsed_jd: JobDescription
    parsed_resume: Resume
    matching_analysis: MatchingResponse
    tone: str = "Professional"
    generate_email: bool = False

class GenerateRequestV1(BaseModel):
    parsed_jd: JobDescription
    parsed_resume: Resume
    tone: str = "Professional"
    generate_email: bool = False
 
 
class GenerateResponse(BaseModel):
    cover_letter: str
    cover_email: str | None = None