from pydantic import BaseModel, Field
from typing import List, Optional

class SearchJobRequest(BaseModel):
    query: str = Field(description="The job title or keywords to search for, e.g., 'Software Engineer'.")
    country: str = Field(description="The 2-letter country code (e.g., 'us', 'in', 'uk').", default="in")
    city: str | None = Field(description="The city to search in, e.g., 'San Francisco'.", default=None)
    employment_types: List[str] = Field(description="List of employment types: FULLTIME, PARTTIME, CONTRACTOR, INTERN", default=["FULLTIME"])
    min_salary: int = Field(description="The minimum annual salary.", default=0)

class SearchJobPromptRequest(BaseModel):
    prompt: str = Field(description="The natural language prompt describing the job search.")
    page: int = 1
    num_pages: int = 1
