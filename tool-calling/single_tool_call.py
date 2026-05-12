from openai import OpenAI 
from dotenv import load_dotenv
import requests

# SETUP THE ENVIRONMENT
load_dotenv()
client = OpenAI()

f = open("weather_tool_description.txt","r")
function_description = f.read()
f.close()

# CREATE FIRST TOOL - WEATHER DATA
def get_weather(zipcode):
    apikey = os.getenv("WEATHER_API_KEY")
    countrycode = "in"
    url = f"https://api.openweathermap.org/data/2.5/weather?zip={ZIP_CODE},{COUNTRY_CODE}&appid={WEATHER_API_KEY}"
    result = requests.get(url)
    response = result.json()
    return response 

# TOOL SCHEMA
openai_tools = [
    {
        "type": "function",
        "name": "get_weather",
        "description": function_description,
        "parameters": {
            "type": "object",
            "properties": {
                "zipcode": {
                    "type": "string",
                    "description": "the zip of the location to get the weather information of."
                },
            },
            "required": ["zipcode"],
        }
    }
]

# ASK FOR USER QUERY
user_query = input("HUMAN QUERY: ")

# CONNECT TO LLM
response = client.responses.create(
    model="gpt-5.4-mini",
    input=user_query,
    tools=openai_tools
)

print(response)

# if type is output_Text, print the output and end the execution
# if type is function_call, run the function, get the output of the function