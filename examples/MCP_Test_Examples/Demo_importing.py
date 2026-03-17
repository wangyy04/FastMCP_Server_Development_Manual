from fastmcp import FastMCP
import asyncio

mcp=FastMCP("Demo")
mcp_a=FastMCP("Demo_a")
mcp_b=FastMCP("Demo_b")

@mcp_a.tool()
async def add(a:int,b:int) -> int:
    """
    将两个整数相加
    Args:
        a:第一个加数
        b:第二个加数
    Return:
        两个数a和b的和
    """
    return a+b

@mcp_b.tool()
async def add(a:int,b:int) -> int:
    """
    将两个整数相加
    Args:
        a:第一个加数
        b:第二个加数
    Return:
        两个数a和b的和
    """
    return a+b+1

@mcp.tool()
async def add(a:int,b:int) -> int:
    """
    将两个整数相加
    Args:
        a:第一个加数
        b:第二个加数
    Return:
        两个数a和b的和
    """
    return a+b+2

async def setup():
    await mcp.import_server(mcp_a)
    await mcp.import_server(mcp_b)

if __name__=="__main__":
    asyncio.run(setup())
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)