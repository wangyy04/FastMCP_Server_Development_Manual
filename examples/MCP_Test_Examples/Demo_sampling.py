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
    prompt=f"确定要计算{a}+{b}吗？确定的话回复“Y”，取消则回复“N”。仅可回复这两个字母中的一个"
    responce = await ctx.sample(prompt)
    ret = responce.text.strip().upper()
    if ret=="Y":
        return a+b
    else:
        return "Calculation is cancelled."

if __name__=="__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)