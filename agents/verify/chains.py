from langchain.agents import create_agent
from langchain.messages import HumanMessage
from models.schema import IsResumeResponse
from agents.verify.prompts import IS_JOB_DESCRIPTION_PROMPT, IS_RESUME_PROMPT


def check_is_resume(llm, resume_text: str) -> bool:
    agent = create_agent(
        model = llm,
        system_prompt = IS_RESUME_PROMPT,
        response_format = IsResumeResponse
    )   
    query = HumanMessage(content = resume_text)
    response = agent.invoke({
        "messages": [query]
    })
    return response['structured_response'].is_resume


def check_is_job_description(llm, job_desc: str) -> bool:
    agent = create_agent(
        model = llm,
        system_prompt = IS_JOB_DESCRIPTION_PROMPT,
        response_format = IsResumeResponse
    )   
    query = HumanMessage(content = job_desc)
    response = agent.invoke({
        "messages": [query]
    })
    return response['structured_response'].is_resume