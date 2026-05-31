from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain_core.runnables import RunnableLambda, RunnableParallel
from models.schema import JobDescription, Resume
from agents.extraction.prompts import JD_PARSER_PROMPT, RESUME_PARSER_PROMPT

def parse_job_description(llm, job_desc: str) -> JobDescription:
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

def parse_resume(llm, resume_text: str) -> Resume:
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