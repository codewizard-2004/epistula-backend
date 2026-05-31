import os
from dotenv import load_dotenv
import requests
from typing import Optional, List

load_dotenv()
RAPID_API_KEY = os.getenv("RAPID_API_KEY")

def search_jobs(query: str, country: str = "us", city: Optional[str] = None, employment_types: Optional[List[str]] = None, min_salary: Optional[int] = None, page: int = 1, num_pages: int = 1):
    """
    Search jobs using JSearch API.

    Args:
        query: Job title/keywords (e.g. "Software Engineer")
        country: Country code (us, in, uk, etc.)
        city: City name
        employment_types: ["FULLTIME", "PARTTIME", "CONTRACTOR", "INTERN"]
        min_salary: Minimum annual salary
        page: Page number
        num_pages: Number of pages to fetch

    Returns:
        JSON response from JSearch API
    """

    url = "https://jsearch.p.rapidapi.com/search"

    params = {
        "query": query,
        "page": page,
        "num_pages": num_pages,
        "country": country,
    }

    if city:
        params["query"] += f" in {city}"
    if employment_types:
        params["employment_types"] = ",".join(employment_types)
    if min_salary:
        params["salary_min"] = min_salary

    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": "jsearch.p.rapidapi.com",
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=30,
    )

    response.raise_for_status()
    return response.json()

