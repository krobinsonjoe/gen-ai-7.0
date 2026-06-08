from dotenv import load_dotenv
from openai import OpenAI
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
import json 

# ENVIRONMENT SETUP
load_dotenv()
client = OpenAI()

# SYSTEM PROMPT FOR MCP
SYSTEM_PROMPT = """
You are an MCP client AI assistant with access to external tools via MCP.

Once you receive the request of the user, check available tools and make
a decision on whether the user query should be answered via a tool or via
internal LLM data.

Based upon your decision, continue answering the query of the user.
"""

# PYTHON FUNCTION TO AUTOMATICALLY GENERATE SCHEMA OF TOOLS
def generate_tool_schema(tool):
    return {
        "type": "function",
        "name": tool.name,
        "description": tool.description or "",
        "parameters": tool.inputSchema
    }

# MAIN MCP CLIENT LOGIC

async def main():
    query = input("Enter Human Query: ")

    async with streamable_http_client("http://localhost:8000/mcp") as (
        read_stream,
        write_stream,
        input_stream,
    ):
         async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tool_list = await session.list_tools()
            print(tool_list)
            tools = tool_list.tools 
            openai_tools = []
            for t in tools:
                openai_tools.append(generate_tool_schema(t))
            response = client.responses.create(
                model="gpt-5.4-mini",
                input=query,
                tools=openai_tools
            )
            tool_call = None
            for item in response.output:
                if item.type == "function_call":
                    tool_call = item 
                    break 
            if tool_call:
                tool_name = tool_call.name 
                args = json.loads(tool_call.arguments)
                print(f"LLM SELECTED TOOL: {tool_name}")
                result = await session.call_tool(tool_name,args)
                print("\nTOOL RESULT\n")
                for item in result.content:
                    print(item.text)
            else:
                print("\nNO TOOL SELECTED, USING INTERNAL LLM DATA\n")
                print(response.output_text)

                
            

asyncio.run(main())