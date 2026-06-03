from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END 
from typing import TypedDict, Optional
import json
from neo4j import GraphDatabase
import os 

# SETUP THE ENVIRONMENT
load_dotenv()
llm = ChatOpenAI(
    model="gpt-5.4-mini"
)

# SETUP THE NEO4J CONNECTION
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

neo4j_driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j",NEO4J_PASSWORD)
)

# DEFINE THE STATE

class ChatState(TypedDict):
    user_id: str 
    user_query: str 
    ai_reply: str 
    store_memory: Optional[bool] # true or false value 
    extracted_facts: Optional[list] #list value because multiple memories can exist from the single input

# NODE 1: CHAT NODE
def chat_node(state: ChatState):
    response = llm.invoke(state['user_query'])
    state['ai_reply'] = response.content 
    print(f"AI REPLY:\n {state['ai_reply']}")
    return state 

# NODE 2: MEMORY CLASSIFIER NODE
def memory_classifier_node(state: ChatState):
    prompt = f"""
You are a user profile memory classifier.

Determine whether this message contains any 
long term personal information about the user.
Return the output in the following JSON format:

{{
    "store": true or false,
    "facts": [list of extracted long term memory facts]
}}

Message:
{state['user_query']}
"""
    response = llm.invoke(prompt)
    decision = json.loads(response.content)
    state['store_memory'] = decision['store']
    state['extracted_facts'] = decision.get('facts',[])
    return state 

# NODE 3: NEO4J SAVE NODE
def neo4j_save_node(state: ChatState):
    if not state['extracted_facts']:
        return state
    else:
        with neo4j_driver.session() as session:
            for fact in state['extracted_facts']:
                session.run(
                    """
                    MERGE (u: User {id: $user_id})
                    MERGE (m: Memory {text: $fact})
                    MERGE (u)-[:HAS_MEMORY]->(m)
                    """,
                    user_id = state['user_id'],
                    fact=fact
                )
        print("found long term data, saving as memory.")
        return state 

# CONDITIONAL ROUTING
def router(state: ChatState):
    if state['store_memory']:
        return "neo4j_save"
    else:
        return END 


# BUILD THE GRAPH

graph = StateGraph(ChatState)

graph.add_node("chat",chat_node)
graph.add_node("memory_classifier",memory_classifier_node)
graph.add_node("neo4j_save",neo4j_save_node)

graph.set_entry_point("chat")
graph.add_edge("chat","memory_classifier")

graph.add_conditional_edges(
    "memory_classifier",
    router,
    {
        "neo4j_save": "neo4j_save",
        END: END 
    }
)

graph.add_edge("neo4j_save", END)

app = graph.compile()

# EXECUTE THE WORKFLOW

def run_chat():
    user_id = input("Enter your ID: ")
    while True:
        user_query = input("Human Question: ")
        if user_query.lower() == "exit":
            break 
        app.invoke({
            "user_id": user_id,
            "user_query": user_query
        })

run_chat()