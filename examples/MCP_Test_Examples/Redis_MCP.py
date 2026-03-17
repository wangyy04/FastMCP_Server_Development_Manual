from fastmcp import FastMCP

mcp=FastMCP("Demo",host="127.0.0.1",port=8000)
# mcp=FastMCP("MCP_Demo",host="0.0.0.0",port=8000)

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
    return a+b

if __name__=="__main__":
    mcp.run(transport="streamable-http")