from fastapi import APIRouter, HTTPException, Depends, Request
from utils.auth import verify_jwt
from utils.limiter import limiter
from services.jobs_search import search_jobs
from models.job_models import SearchJobPromptRequest
from agents.job.chains import parse_job_search_prompt

router = APIRouter(
    prefix="/api/jobs",
    tags=["Jobs"],
    dependencies=[Depends(verify_jwt)]
)


@router.post("/search", response_model = dict)
@limiter.limit("10/minute")
async def search(body: SearchJobPromptRequest, request: Request):
    """
    Search jobs using JSearch API.

    Args:
        body (SearchJobPromptRequest): The request body containing the natural language prompt, page number, and number of pages.

    Returns:
        dict: A JSON object containing the search results.
    """
    try:
        parsed_params = parse_job_search_prompt(request.app.state.google_llm, body.prompt)
        
        result = search_jobs(
            parsed_params.query,
            parsed_params.country,
            parsed_params.city,
            parsed_params.employment_types,
            parsed_params.min_salary,
            body.page,
            body.num_pages,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {e}")

    