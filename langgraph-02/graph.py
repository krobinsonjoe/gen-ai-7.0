from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END 
from typing import TypedDict

# SETUP THE ENVIRONMENT
load_dotenv()

llm_developer = ChatOpenAI(
    model="gpt-5.4"
)

llm_qa = ChatOpenAI(
    model="gpt-5.5"
)

MAX_RETRIES = 3

# DEFINE THE STATE

class CodeState(TypedDict):
    user_request: str 
    code: str 
    rating: int 
    feedback: str 
    retries: int 
    status: str 

# AGENT 1: DEVELOPER AGENT
def developer_agent(state: CodeState):
    prompt = f"""
You are a python developer.
Write python code following the requirements of the user:
{state['user_request']}

If feedback is provided, improve the previous version of the code.
Previous Code:
{state['code']}

Feedback:
{state['feedback']}

Return ONLY the full python code.
"""
    result = llm_developer.invoke(prompt).content.strip()
    return {
        "code": result,
        "feedback": ""
    }

# AGENT 2: QA AGENT
def qa_agent(state: CodeState):
    prompt = f"""
You a senior Python QA Engineer.
Evaluate the following Python code for the given requirements:
- Correctness of the code
- Structure of the code
- Readability of the code
- Whether the code is following global best practices
- The error handling capabilities of the code
- The scalability factor in the code if required to scale in the future
- Packages the code is using and if they are globally accepted packages

Return output in the following JSON format:
{{
    "rating": integer value between 1-10,
    "feedback": string value with clear explanation of what improvements to make to the code
}}

Code:
{state['code']}
"""
    result = llm_qa.invoke(prompt).content.strip()
    return {
        "rating": int(result['rating']),
        "feedback": result['feedback']
    }

# NODE: SET APPROVED
def set_approved(state: CodeState):
    return {"status": "approved"}

# NODE: SET FAILED
def set_failed(state: CodeState):
    return {"status": "failed"}

# NODE: INCREMENTAL RETRY LOGIC
def increment_retry(state: CodeState):
    return {"retries": state['retries']+1}

# NODE: ROUTE LOGIC
def check_rating(state: CodeState):
    if state['rating'] >= 7:
        return "approved"
    if state['retries'] >= MAX_RETRIES:
        return "failed"
    return "retry"