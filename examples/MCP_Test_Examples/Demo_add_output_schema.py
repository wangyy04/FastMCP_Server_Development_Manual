from fastmcp import FastMCP

mcp=FastMCP("Demo_add",host="0.0.0.0",port=8000)

@mcp.tool(output_schema={
    "type": "object",
    "properties": {
        "args_1": {
            "type": "integer",
            "description": "The argument a"
        },
        "args_2": {
            "type": "integer",
            "description": "The argument b"
        },
        "ret": {
            "type": "integer",
            "description": "The sum of a and b",
            "minimum": -2147483648,
            "maximum": 2147483647
        }
    },
    "required": ["args_1","args_2","ret"]
})
async def add(a:int,b:int) -> dict:
    """
    将两个整数相加
    Args:
        a:第一个加数
        b:第二个加数
    Return:
        两个数a和b的和
    """
    return {
        "args_1": a,
        "args_2": b,
        "ret": a+b
    }

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