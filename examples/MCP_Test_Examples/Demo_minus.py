from fastmcp import FastMCP

mcp=FastMCP("Demo_minus",host="0.0.0.0",port=8080)

@mcp.tool()
async def minus(a:int,b:int) -> int:
    """
    将两个整数相减
    Args:
        a:被减数
        b:减数
    Return:
        a减b的差
    """
    return a-b

if __name__=="__main__":
    mcp.run(transport="streamable-http")