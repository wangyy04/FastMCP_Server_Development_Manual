from fastmcp import FastMCP
from fastmcp.resources import TextResource

# mcp=FastMCP("Demo")
mcp=FastMCP("Demo", host="127.0.0.1", port=8000)

special_resource = TextResource(uri="resource://special-data",
                                text="Hello world")
mcp.add_resource(special_resource, key="internal://data-v2")
mcp.add_resource(special_resource, key="file://data-v2")

if __name__=="__main__":
    # mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
    mcp.run(transport="sse")