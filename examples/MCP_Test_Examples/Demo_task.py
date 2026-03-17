from fastmcp import FastMCP
from fastmcp.server.tasks import TaskConfig
import asyncio

mcp=FastMCP("Demo_add")

@mcp.tool(task=TaskConfig())
async def add(a:int,b:int) -> int:
    """
    将两个整数相加
    Args:
        a:第一个加数
        b:第二个加数
    Return:
        两个数a和b的和
    """
    await asyncio.sleep(10)
    return a+b

if __name__=="__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)