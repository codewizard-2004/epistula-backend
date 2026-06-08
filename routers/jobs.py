from fastapi import APIRouter, HTTPException, Depends, Request
from utils.auth import verify_jwt
from utils.limiter import limiter
from services.jobs_search import search_jobs
from models.schema import SearchJobRequest

router = APIRouter(
    prefix="/api/jobs",
    tags=["Jobs"],
    dependencies=[Depends(verify_jwt)]
)


@router.post("/search", response_model = dict)
@limiter.limit("10/minute")
async def search(body: SearchJobRequest, request: Request):
    """
    Search jobs using JSearch API.

    Args:
        body (SearchJobRequest): The request body containing the query, country, city, employment types, minimum salary, page number, and number of pages.

    Returns:
        dict: A JSON object containing the search results.
    """
    try:
        result = search_jobs(
            body.query,
            body.country,
            body.city,
            body.employment_types,
            body.min_salary,
            body.page,
            body.num_pages,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {e}")

    