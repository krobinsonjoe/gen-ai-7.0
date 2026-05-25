from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END 
from typing import TypedDict

# SETUP THE ENVIRONMENT
load_dotenv()

llm = ChatOpenAI(
    model="gpt-5.4-mini"
)

# DEFINE THE STATE
class SupportState(TypedDict):
    user_query: str 
    intent: str 
    response: str 

# AGENT 1: INTENT CLASSIFIER AGENT
def classify_intent(state: SupportState):
    prompt = f"""
Classify the user query into one of these categories:
- password_reset
- order_tracking
- refund

Only return the category name.

User Query: {state['user_query']}
"""
    result = llm.invoke(prompt)
    return {"intent": result.content.strip().lower()}


# AGENT 2: REFUND AGENT
def handle_refund(state: SupportState):
    return {
        "response": (
            "Refund request received, will be credited in 3 working days."
        )
    }

# AGENT 3: ORDER TRACKING AGENT
def handle_order(state: SupportState):
    return {
        "response": (
            "Please click on my orders under your profile to track your order."
        )
    }

# AGENT 4: PASSWORD RESET AGENT
def handle_password(state: SupportState):
    return {
        "response": (
            "An email has been sent to you to reset your password."
        )
    }

# ROUTER FUNCTION

def route_intent(state: SupportState):
    if state['intent'] == "password_reset":
        return "password_node"
    elif state['intent'] == "order_tracking":
        return "order_node"
    elif state['intent'] == "refund":
        return "refund_node"
    else:
        return END 
    
# BUILDING MY AI GRAPH WORKFLOW

graph = StateGraph(SupportState)

graph.add_node("classifier",classify_intent)
graph.add_node("password_node", handle_password)
graph.add_node("order_node", handle_order)
graph.add_node("refund_node", handle_refund)

graph.set_entry_point("classifier")

graph.add_conditional_edges("classifier",route_intent)

graph.add_edge("password_node", END)
graph.add_edge("order_node", END)
graph.add_edge("refund_node", END)

app = graph.compile()


# EXECUTE THE GRAPH

user_input = input("Enter Query: ")

result = app.invoke({
    "user_query": user_input,
    "intent": "",
    "response": ""
})

print(result['response'])