from openai import OpenAI 
from dotenv import load_dotenv 

# SETUP THE ENVIRONMENT
load_dotenv()
client = OpenAI()

# ASK FOR USER INPUT
user_query = input("Human Query: ")

# CONNECT TO THE LLM
response = client.responses.create(
    model="gpt-5.4-mini",
    input=[
        {
            "role": "user",
            "content": "hi, my name is aryan."
        },
        {
            "role": "assistant",
            "content": "Hi Aryan — nice to meet you! How can I help you today?"
        },
        {
            "role": "user",
            "content": user_query
        }
    ]
)

print("\nAI REPLY\n")
print(response.output_text)