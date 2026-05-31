from langchain.agents import create_agent
from langchain.messages import HumanMessage
from models.schema import JobDescription, Resume, MatchingResponse, ATSResponse
from langchain_core.runnables import RunnableLambda, RunnableParallel
from agents.analysis.prompts import MATCH_ANALYZER_PROMPT, ATS_CHECKER_PROMPT
from models.analyze_models import QuickMatchingResponse

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

def quick_analyze_match(llm, job_desc: JobDescription, resume: Resume) -> int:
    """
    This agent will take the job description and resume in json format and analyze how well the resume matches the job description.
    
    Args:
        llm: The language model instance to use for analysis.
        job_desc (JobDescription)
        resume (Resume)
    Return:
        int: The matching percentage.
    """
    agent = create_agent(
        model = llm,
        system_prompt = "You are a useful AI agent that takes the parsed information from resume and parsed information from job description as input and returns only the matching percentage between them in integer format.",
        response_format = QuickMatchingResponse
    )

    query1 = HumanMessage(content = job_desc.model_dump_json(indent=2))
    query2 = HumanMessage(content = resume.model_dump_json(indent=2))
    response = agent.invoke({
        "messages": [query1, query2]
    })

    return response['structured_response'].matching_percentage

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