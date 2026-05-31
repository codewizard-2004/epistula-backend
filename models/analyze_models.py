from pydantic import BaseModel
from models.schema import JobDescription, Resume, MatchingResponse, ATSResponse

class AnalyzeRequest(BaseModel):
    parsed_jd: JobDescription
    parsed_resume: Resume
    raw_resume: str

class AnalyzeResponse(BaseModel):
    match_analysis: MatchingResponse
    ats_result: ATSResponse

class MatchingRequest(BaseModel):
    jd: str
    parsed_resume: Resume

class MatchingResponse(BaseModel):
    status: str
    matching_percentage: int

class QuickMatchingResponse(BaseModel):
    matching_percentage: int