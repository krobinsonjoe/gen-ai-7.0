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

@mcp.tool()
def fake_tool(stock_name: str):
    """
    This is a tool which provides us with financial information of any stock
    of the past 6 months. For this tool to run, it requires the name 
    of the particular stock and it connects to external data sources to find out
    information related to the particular stock.
    """
    return {
        "Stock": stock_name,
        "Price": "10 USD"
    }

mcp.run(transport="streamable-http")