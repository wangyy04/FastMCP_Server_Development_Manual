from fastmcp import FastMCP,Context

mcp=FastMCP("Demo_logging",host="127.0.0.1",port=8000)

@mcp.tool()
async def add(a:int,b:int,ctx:Context) -> int:
    """
    将两个整数相加
    Args:
        a:第一个加数
        b:第二个加数
        ctx:日志Context
    Return:
        两个数a和b的和
    """
    await ctx.debug(f"my_debug_log {a} and {b}")
    await ctx.info(f"my_info_log {a} and {b}")
    await ctx.warning(f"my_warning_log {a} and {b}")
    await ctx.error(f"my_error_log {a} and {b}")
    return a+b

if __name__=="__main__":
    mcp.run(transport="streamable-http")