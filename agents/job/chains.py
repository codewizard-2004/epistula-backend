from langchain.agents import create_agent
from langchain.messages import HumanMessage
from models.job_models import SearchJobRequest
from agents.job.prompts import JOB_SEARCH_PROMPT

def parse_job_search_prompt(llm, prompt: str) -> SearchJobRequest:
    """
    Extracts job search parameters from a natural language prompt.
    Args:
        llm: The language model instance to use.
        prompt: The user's natural language search query.
    Returns:
        SearchJobRequest object containing extracted search parameters.
    """
    agent = create_agent(
        model=llm,
        system_prompt=JOB_SEARCH_PROMPT,
        response_format=SearchJobRequest
    )

    query = HumanMessage(content=prompt)
    response = agent.invoke({
        "messages": [query]
    })

    return response['structured_response']