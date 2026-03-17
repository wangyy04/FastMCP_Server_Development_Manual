from fastmcp import FastMCP, Context

mcp=FastMCP("Demo_add")

@mcp.tool()
async def add(a:int,b:int,ctx:Context):
    """
    将两个整数相加
    Args:
        a:第一个加数
        b:第二个加数
    Return:
        两个数a和b的和
    """
    mes = f"确定要计算{a}+{b}吗？回答”yes”以计算"
    responce = await ctx.elicit(message=mes,
                                response_type=str)
    if responce.action=="yes":
        return a+b
    else:
        return "Calculation is cancelled."

if __name__=="__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)