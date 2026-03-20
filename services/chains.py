"""
THIS WILL CONTAIN ALL THE LANGCHAIN PIPELINES
1) FOR PARSING RESUME
2) FOR PARSING JOB DESCRIPTION
3) ATS CHECKING
4) MATCHING CHECKING
5) SCRAPPING
"""

from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from services.prompts import JD_PARSER_PROMPT, RESUME_PARSER_PROMPT, MATCH_ANALYZER_PROMPT, ATS_CHECKER_PROMPT, COVER_LETTER_GENERATOR_PROMPT, COVER_EMAIL_GENERATOR_PROMPT
from models.schema import JobDescription, Resume, MatchingResponse, ATSResponse

def parse_job_description(llm: ChatGoogleGenerativeAI, job_desc: str) -> JobDescription:
    """
    This agent will take the job description as input and will return the parsed output in JobDescription format.
    Args:
        llm: The language model instance to use for parsing the job description.
        job_desc: The job description as a string.
    Returns:
        A JobDescription object containing the parsed information from the job description.
    """
    agent = create_agent(
        model = llm,
        system_prompt = JD_PARSER_PROMPT,
        response_format = JobDescription
    )

    query = HumanMessage(content = job_desc)
    response = agent.invoke({
        "messages": [query]
    })
    return response['structured_response']


def parse_resume(llm: ChatGoogleGenerativeAI, resume_text: str) -> Resume:
    """
    This agent will take the resume text as input and will return the parsed output in Resume format.
    Args:
        llm:(ChatGoogleGenerativeAI) llm instance to be used
        resume_text: (str) the resume text to be parsed
    Returns:
        Resume: The resume in structured json format as defined in the Resume model
    """
    agent = create_agent(
        model = llm,
        system_prompt = RESUME_PARSER_PROMPT,
        response_format = Resume
    )
    query = HumanMessage(content = resume_text)
    response = agent.invoke({
        "messages": [query]
    })
    return response['structured_response']

def analyze_match(llm, job_desc: JobDescription, resume: Resume) -> MatchingResponse:
    """
    This agent will take the job description and resume in json format and analyze how well the resume matches the job description.
    
    Args:
        llm: The language model instance to use for analysis.
        job_desc (JobDescription)
        resume (Resume)
    Return:
        MatchingResponse: A JSON object containing the match percentage and a list of matching and non-matching skills, experience, education etc.
    """
    agent = create_agent(
        model = llm,
        system_prompt = MATCH_ANALYZER_PROMPT,
        response_format = MatchingResponse
    )

    query1 = HumanMessage(content = job_desc.model_dump_json(indent=2))
    query2 = HumanMessage(content = resume.model_dump_json(indent=2))
    response = agent.invoke({
        "messages": [query1, query2]
    })

    return response['structured_response']

def check_ats(llm, resume: str) -> ATSResponse:
    """
    This agent will take the resume in string format and analyze how well it is optimized for ATS.
    Args:
        llm: The language model instance to use for analysis.
        resume (string): The resume text to analyze.
    Return:
        ATSResponse: a json response containing ATS score and suggestions
    """
    agent = create_agent(
        model = llm,
        system_prompt = ATS_CHECKER_PROMPT,
        response_format = ATSResponse
    )
    query = HumanMessage(content = resume)

    response = agent.invoke({
        "messages": [query]
    })

    return response['structured_response']

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
    query3 = HumanMessage(content = match_response.model_dump_json(indent=2))
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

def run_generation_pipeline():
    pass

def extract_job_search_query():
    pass