from langchain.agents import create_agent
from langchain.messages import HumanMessage
from models.schema import JobDescription, Resume, MatchingResponse
from agents.generation.prompts import COVER_LETTER_GENERATOR_PROMPT, COVER_EMAIL_GENERATOR_PROMPT

def generate_cover_letter(llm, job_desc: JobDescription, resume: Resume, match_response: MatchingResponse, tone: str = "Professional") -> str:
    """
    This agent will take the job description and resume in json format and the match response and generate a cover letter that is tailored to the job description and highlights the skills and experience that match the job description.
    Args:
        llm: The language model instance to use for analysis.
        job_desc (JobDescription)
        resume (Resume)
        match_response (MatchingResponse)
    Return:
        str: A cover letter that is tailored to the job description and highlights the skills and experience that match the job description.
    """

    agent = create_agent(
        model = llm,
        system_prompt = COVER_LETTER_GENERATOR_PROMPT
    )

    query1 = HumanMessage(content=job_desc.model_dump_json(indent=2))
    query2 = HumanMessage(content = resume.model_dump_json(indent=2))
    if match_response:
        query3 = HumanMessage(content = match_response.model_dump_json(indent=2))
    else:
        query3 = HumanMessage(content = "No match response provided, generate a cover letter based on the job description and resume provided.")
    query4 = HumanMessage(content = f"The tone of the cover letter should be {tone} tone")

    response = agent.invoke({
        "messages": [query1, query2, query3, query4]
    })

    return response["messages"][4].content[0]["text"]

def generate_cover_email(llm, job_desc: JobDescription, resume: Resume, match_response: MatchingResponse) -> str:
    """
    This agent will take the job description and resume in json format and the match response and generate a cover email that is tailored to the job description and highlights the skills and experience that match the job description.
    Args:
        llm: The language model instance to use for analysis.
        job_desc (JobDescription)
        resume (Resume)
        match_response (MatchingResponse)
    Return:
        str: A cover email that is tailored to the job description and highlights the skills and experience that match the job description.
    """
    agent = create_agent(
        model = llm,
        system_prompt = COVER_EMAIL_GENERATOR_PROMPT
    )

    query1 = HumanMessage(content=job_desc.model_dump_json(indent=2))
    query2 = HumanMessage(content = resume.model_dump_json(indent=2))
    query3 = HumanMessage(content = match_response.model_dump_json(indent=2))

    response = agent.invoke({
        "messages": [query1, query2, query3]
    })

    return response["messages"][3].content[0]["text"]