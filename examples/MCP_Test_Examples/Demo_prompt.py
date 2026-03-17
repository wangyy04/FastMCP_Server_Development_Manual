from fastmcp import FastMCP
from fastmcp.prompts.prompt import Message, PromptResult, PromptMessage, TextContent

mcp=FastMCP("Demo", host="0.0.0.0", port=8000, on_duplicate_prompts="replace")

@mcp.prompt(name="greeting")
def greeting_a(name: str):
    """
    生成问候语提示词
    """
    return PromptMessage(role="user",content=TextContent(type="text",text=f"Hello, {name}!A"))

@mcp.prompt(name="greeting")
def greeting_b(name: str):
    """
    生成问候语提示词
    """
    return Message(f"Hello, {name}!B")

if __name__=="__main__":
    mcp.run(transport="streamable-http")