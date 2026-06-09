from openai import OpenAI
from dotenv import load_dotenv

# SETUP THE ENVIRONMENT
load_dotenv()
client = OpenAI()

SYSTEM_PROMPT = """
You are an AI meeting notes assistant.
You will receive raw meeting notes containing
interruptions, filler words and other common speech to text issues.

Please convert these notes into a professional summary which can 
be shared with stakeholders.
"""

def summarize(notes):
    response = client.responses.create(
        model="gpt-5.4-mini",
        instructions=SYSTEM_PROMPT,
        input=notes
    )
    return response.output_text

f = open("raw_meeting_notes.txt","r")
raw_meeting_notes = f.read()
f.close()

summary = summarize(notes=raw_meeting_notes)
print(summary)