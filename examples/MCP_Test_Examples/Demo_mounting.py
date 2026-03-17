from fastmcp import FastMCP
from contextlib import asynccontextmanager
from fastmcp.utilities.logging import get_logger
import logging

logger = get_logger(name="logger")
logger.setLevel(level=logging.DEBUG)

@asynccontextmanager
async def mcp_lifespan(server: FastMCP):
    logger.debug(f"{server.name} start.")
    try:
        logger.debug(f"{server.name} is running.")
        yield
    finally:
        logger.debug(f"{server.name} shut down.")

mcp=FastMCP("Demo", lifespan=mcp_lifespan)
mcp_a=FastMCP("Demo_a", lifespan=mcp_lifespan)
mcp_b=FastMCP("Demo_b", lifespan=mcp_lifespan)

@mcp_a.tool()
async def add(a:int,b:int) -> int:
    """将两个整数相加"""
    return a+b

@mcp_b.tool()
async def add1(a:int,b:int) -> int:
    """将两个整数相加+1"""
    return a+b+1

@mcp.tool()
async def add2(a:int,b:int) -> int:
    """将两个整数相加+2"""
    return a+b+2

mcp.mount(mcp_a,as_proxy=True)
mcp.mount(mcp_b,as_proxy=True)

if __name__=="__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)