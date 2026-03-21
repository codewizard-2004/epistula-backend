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
from models.schema import JobDescription, Resume, MatchingResponse, ATSResponse, ParallelParsingOutput
from langchain_core.runnables import RunnableLambda, RunnableParallel

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

def parsing_in_parallel(llm, job_desc: str, resume_text: str):
    """
    This agent parallely executes the parsing of job description and resume and returns the parsed output in a single response.
    This is more efficient than executing them sequentially as it reduces the overall latency by leveraging the ability of the language model to handle multiple tasks in parallel.

    Args:
        llm: The language model instance to use for parsing.
        job_desc: The job description as a string.
        resume_text: The resume text as a string.
    Returns:
        A dictionary containing the parsed job description and resume. 
        Contains keywords parsed_jd(JDKeywords), parsed_resume(Resume) and raw_resume(str).
    """
    parse_jd_runnable = RunnableLambda(
        lambda x: parse_job_description(llm, x["job_desc"])#type: ignore
    )
    parse_resume_runnable = RunnableLambda(
        lambda x: parse_resume(llm, x["resume"])#type: ignore
    )

    # 2. Bundle them into a Parallel runner
    parsing_step = RunnableParallel({
        "parsed_jd": parse_jd_runnable,
        "parsed_resume": parse_resume_runnable,
        "raw_resume": RunnableLambda(lambda x: x["resume"]) # type: ignore
    })

    # 3. Invoke with the initial dictionary
    response = parsing_step.invoke({
        "job_desc": job_desc,
        "resume": resume_text
    })
    
    return response

def analysis_in_parallel(llm, job_desc: JobDescription, resume: Resume, raw_resume: str):
    """
    This function will parallely run the matching analysis and ATS checking and return the response in a single dictionary.
    This is faster than running them sequentially as it reduces the overall latency by leveraging the ability of the language model to handle multiple tasks in parallel.

    Args:
        llm: The language model instance to use for analysis.
        job_desc (JobDescription)
        resume (Resume)
        raw_resume (str): The raw resume text to be used for ATS checking.
    Return:
        A dictionary containing the matching analysis response and ATS checking response.
        Contains keywords matching_analysis(MatchingResponse) and ats_result(ATSResponse).
    """
    matching_runnable = RunnableParallel({
        "matching_analysis": RunnableLambda(lambda x: analyze_match(llm, x["job_desc"], x["resume"])), # type: ignore
        "ats_result": RunnableLambda(lambda x: check_ats(llm, x["raw_resume"])) # type: ignore
    })

    response = matching_runnable.invoke({
        "job_desc": job_desc,
        "resume": resume,
        "raw_resume": raw_resume
    })

    return response

def extract_job_search_query():
    pass