from mcp.server.fastmcp import FastMCP
import wikipedia

mcp = FastMCP("Information MCP Server", json_response=True)

@mcp.tool()
def wikipedia_search(topic: str):
    """
    Get wikipedia summary of any topic by providing the relevant
    topic name. This wikipedia search tool is limited to only providing
    a 10 line summary of the given topic.
    """
    try:
        return wikipedia.summary(topic,sentences=10)
    except Exception as e:
        return str(e)

@mcp.tool()
def database_search(name: str):
    """
    Search company data for information on a given person. For this tool
    to successfully work, it will require the name of the person to search
    for in the database. It will provide basic information such as 
    name, date of birth, years of employment, designation for that person.
    """
    return {
        "name": name,
        "DOB": "29/06/1998",
        "YOE": 9,
        "Designation": "Engineer"
    }

mcp.run(transport="streamable-http")