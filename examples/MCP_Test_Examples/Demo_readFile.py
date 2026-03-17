# from fastmcp import FastMCP
#
# mcp=FastMCP("Demo_readFile", host="0.0.0.0", port=8000)
#
# @mcp.tool()
# async def add_with_file(a:int,b:int) -> int:
#     """
#     将两个整数相加后加上服务器指定的值
#     Args:
#         a:第一个加数
#         b:第二个加数
#     Return:
#         a、b和服务器指定值的和
#     """
#     file_path="./test_file.txt"
#     with open(file_path,'r') as file:
#         c=int(file.read().strip())
#     return a+b+c
#
# if __name__=="__main__":
#     mcp.run(transport="streamable-http")


from fastmcp import FastMCP,Context
from pathlib import Path
from fastmcp.resources import FileResource

mcp=FastMCP("Demo_readFile", host="0.0.0.0", port=8000)

file_path = Path("./test_file.txt").resolve()
file_resource = FileResource(
    uri=f"file://{file_path.as_posix()}",  # 使用as_posix()确保路径格式正确
    path=file_path,
    name="My fext file",
    mime_type="text/plain",
)
mcp.add_resource(file_resource)  # 将资源添加到MCP实例

@mcp.tool(exclude_args=["doc_uri"])
async def add_with_file(a : int,b : int,ctx : Context, doc_uri: str = file_resource.uri) -> int:
    """
    将两个整数相加后加上服务器指定的值
    Args:
        a:第一个加数
        b:第二个加数
    Return:
        a、b和服务器指定值的和
    """
    doc_resource = await ctx.read_resource(uri=doc_uri)
    doc_content = doc_resource[0].content
    c = int(doc_content)
    return a+b+c

if __name__=="__main__":
    mcp.run(transport="streamable-http")