from fastmcp import FastMCP
from pathlib import Path
from fastmcp.resources import TextResource, BinaryResource, FileResource, HttpResource, DirectoryResource, \
    FunctionResource

mcp=FastMCP("Demo_resource",on_duplicate_resources="ignore")

@mcp.resource("resource://greeting")
def get_greeting() -> str:
    """
    提供一句简单的问候语
    Return:
        问候语
    """
    return "Hello world!"

@mcp.resource("api://{endpoint}{?version,limit,offset}")
def call_api(endpoint: str, version: int = 1, limit: int = 10, offset: int = 0) -> dict:
    """调用带有分页的API端点。"""
    return {
        "endpoint": endpoint,
        "version": version,
        "limit": limit,
        "offset": offset
    }

a=TextResource(uri="resource://notice",
    name="Important Notice",
    text="System maintenance scheduled for Sunday.",
    title="test",
    description="This is a test",
    tags={"notification"})
b=BinaryResource(uri="resource://aaa",data=b'hello')
c=FileResource(uri="resource://myFile",
               path=Path("./resource_test.txt").resolve())
# d=HttpResource(uri="resource://test_website",
#                url="https://gofastmcp.com/v2/getting-started/welcome.md",
#                mime_type="text/markdown")
d=HttpResource(uri="resource://test_website",
               url="https://gofastmcp.com/v2/getting-started/welcome",
               mime_type="application/json")
e=DirectoryResource(uri="directory://test",
                    path=Path("./DirectoryResource_test").resolve(),
                    recursive=False,
                    pattern="*.in")
# mcp.add_resource(a)
# mcp.add_resource(b)
# mcp.add_resource(c)
# mcp.add_resource(d)
# mcp.add_resource(e)

special_resource_1 = TextResource(uri="resource://special-dataA",
                                name="testNameA",
                                key="internal://data-v2A",
                                text="Hello world.")
special_resource_2 = TextResource(uri="resource://special-dataB",
                                key="internal://data-v2B",
                                text="Hello world.")
special_resource_3 = TextResource(uri="resource://special-dataC",
                                name="testNameC",
                                text="Hello world.")
special_resource_4 = TextResource(uri="resource://special-dataD",
                                text="Hello world.")
mcp.add_resource(special_resource_1)
mcp.add_resource(special_resource_2)
mcp.add_resource(special_resource_3)
mcp.add_resource(special_resource_4)

if __name__=="__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)