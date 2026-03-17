from fastmcp.resources import TextResource
from fastmcp import FastMCP

mcp=FastMCP("Demo")

special_resource_1 = TextResource(uri="resource://special-dataA",
                                name="testNameA",
                                text="Hello world.")
special_resource_2 = TextResource(uri="resource://special-dataB",
                                text="Hello world.")
special_resource_3 = TextResource(uri="resource://special-dataC",
                                name="testNameC",
                                text="Hello world.")
special_resource_4 = TextResource(uri="resource://special-dataD",
                                text="Hello world.")
mcp.add_resource(special_resource_1,key="internal://data-v2A")
mcp.add_resource(special_resource_2,key="internal://data-v2B")
mcp.add_resource(special_resource_3)
mcp.add_resource(special_resource_4)

if __name__=="__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)