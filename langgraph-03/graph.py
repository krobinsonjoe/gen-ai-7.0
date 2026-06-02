from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END 
from typing import TypedDict
import json
from langgraph.checkpoint.mongodb import MongoDBSaver
from pymongo import MongoClient


# SETUP THE DATABASE

client = MongoClient("mongodb://localhost:27017")


# SETUP THE ENVIRONMENT
load_dotenv()

llm_developer = ChatOpenAI(
    model="gpt-5.4-nano"
)

llm_qa = ChatOpenAI(
    model="gpt-5.5"
)

MAX_RETRIES = 3

# CREATE FUNCTION TO CONVERT EVERYTHING TO JSON
def llm_json(prompt):
    response = llm_qa.invoke(
        "Return only valid JSON, no markdown.\n" + prompt
    ).content.strip()
    return json.loads(response)

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
Write intentionally bad python code following the requirements of the user:
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
IMPORTANT: Return only valid JSON. No Markdown.

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
    result = llm_json(prompt)
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

# BUILD YOUR GRAPH

graph = StateGraph(CodeState)

# ASSIGN A NAME TO EVERY NODE

graph.add_node("developer",developer_agent)
graph.add_node("qa",qa_agent)
graph.add_node("approved_node", set_approved)
graph.add_node("failed_node", set_failed)
graph.add_node("retry_increment", increment_retry)

# DECIDE THE STARTING POINT OF YOUR WORKFLOW

graph.set_entry_point("developer")

# FLOW OF DATA IN THE WORKFLOW 

graph.add_edge("developer","qa")
graph.add_conditional_edges(
    "qa",
    check_rating,
    {
        "approved": "approved_node",
        "failed": "failed_node",
        "retry": "retry_increment"
    }
)
graph.add_edge("approved_node", END)
graph.add_edge("failed_node", END)
graph.add_edge("retry_increment","developer")

# SETUP MONGODB CHECKPOINTING
mongodb_checkpointer = MongoDBSaver(client)

# COMPILE THE WORKFLOW
app = graph.compile(checkpointer=mongodb_checkpointer)

thread_id = "2"
user_id = "1"

# CHECK IF THREAD IS ALREADY EXISTING IN DB
existing = mongodb_checkpointer.get({
    "configurable": {
        "thread_id": thread_id,
        "user_id": user_id
    }
})

# LOGIC FOR IF THREAD ID IS FOUND
try:
    if existing:
        print("\nRESUMING FROM CHECKPOINT\n")
        result = app.invoke({},config={"configurable": {"thread_id": thread_id, "user_id": user_id}})
    else:
        user_input = input("Enter Python App To Create: ")
        result = app.invoke({
            "user_request": user_input,
            "code": "",
            "rating": 0,
            "feedback": "",
            "retries": 0,
            "status": "running"
        },config={"configurable": {"thread_id": thread_id, "user_id": user_id}})
    print("FINAL RESULT")
    print(f"Code: {result['code']}")
    print(f"Rating: {result['rating']}")
    print(f"Retries Used: {result['retries']}")
    print(f"Feedback: {result['feedback']}")
    print(f"Status: {result['status']}")
except Exception as e:
    print(f"ERROR: {e}")