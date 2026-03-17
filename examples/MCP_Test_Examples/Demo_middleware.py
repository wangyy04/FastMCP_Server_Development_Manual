import logging
from fastmcp import FastMCP
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.utilities.logging import get_logger

mcp = FastMCP("Demo")
logger = get_logger(name="logger")
logger.setLevel(level=logging.DEBUG)

class MyMiddleware(Middleware):
    async def on_message(self, context: MiddlewareContext, call_next):
        logger.info("on_message_1")
        result = await call_next(context)
        logger.info("on_message_2")
        return result

    async def on_request(self, context: MiddlewareContext, call_next):
        logger.info("on_request_1")
        result = await call_next(context)
        logger.info("on_request_2")
        return result

    async def on_list_tools(self, context: MiddlewareContext, call_next):
        logger.info("on_list_tools_1")
        result = await call_next(context)
        logger.info("on_list_tools_2")
        return result
mcp.add_middleware(MyMiddleware())

if __name__=="__main__":
    mcp.run(transport="streamable-http",
            host="0.0.0.0",
            port=8000)