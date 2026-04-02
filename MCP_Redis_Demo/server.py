from fastmcp import FastMCP, Context
from authentication.access_control_list.ACLMiddleware import ACLMiddleware
from pathlib import Path
from contextlib import asynccontextmanager
import redis.asyncio as redis
from typing import Literal
from datetime import datetime
from simpleeval import simple_eval
import re
from starlette.requests import Request
from starlette.responses import JSONResponse
import time

# 日志记录器设置
from fastmcp.utilities.logging import get_logger
import logging
logger = get_logger(name="logger")
logger.setLevel(level=logging.DEBUG)

# 定义生命周期钩子 初始化时建立redis连接
@asynccontextmanager
async def mcp_lifespan(server: FastMCP):
    redis_pool = redis.ConnectionPool(host="127.0.0.1", port=6379,
                                      db=0, decode_responses=True)
    db = redis.Redis(connection_pool=redis_pool)
    try:
        yield {"db": db}
    finally:
        await db.aclose()

mcp = FastMCP("MCP_Redis_Demo", lifespan=mcp_lifespan, exclude_tags={'debug'})

# 添加身份验证（使用ACL）中间件
key_dir = Path("./authentication/access_control_list/private_key").resolve()
mcp.add_middleware(ACLMiddleware(directory=key_dir, method="query"))

# 添加健康检查自定义路由（端点为/heath）
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    try:
        # 尝试连接Redis后端
        rdp = redis.ConnectionPool(host="127.0.0.1", port=6379,
                                  db=0, decode_responses=True,)
        r = redis.Redis(connection_pool=rdp)
        await r.ping()
        # 若能连接到Redis后端，状态200
        redis_status = "connected"
        status_code = 200
        status_message = "200 OK"
        status = "healthy"
        await rdp.disconnect()
    except Exception:
        # 若未能连接Redis后端，状态503
        redis_status = "unconnected"
        status_code = 503
        status_message = "503 Service Unavailable"
        status = "unhealthy"
    return JSONResponse(
        status_code=status_code,
        content={
            "status": status,
            "status_message": status_message,
            "version": mcp.version,
            "timestamp": time.time(),
            "checks": {
                "MCP": "connected",
                "Redis": redis_status
            }
        }
    )

@mcp.prompt()
async def system_prompt(usr_id: str):
    """
    系统提示词，提供基础信息，并指导大模型正确调用工具
    Args:
        usr_id (str): 用户唯一标识
    Return:
        系统提示词
    """
    prompt = (f"你是一个助手，用户的唯一标识为“{usr_id}”，在调用工具时，如有必要则提供。"
              f"你在你觉得必要时，就可以调用工具将键值对存储到Redis数据库，实现长期记忆和跨对话存储。"
              f"当用户表现得像之前告诉过你某些信息，但你在上下文中不记得有这些信息时，你要先调用工具从Redis数据库读取键值对，如果数据库里真的没有所需数据，再问用户。"
              f"如果用户让你记下某信息，或问你记得什么，那就是指Redis数据库相关操作。"
              f"涉及相对时间表述（如“今天”、“明天”、“十天后”）的信息时，不应直接存储这些模糊描述，而应该调用工具，计算出具体时间后，用具体时间替代存储。"
              f"涉及时间敏感的数据，例如行程、车票等，应当在存储的键中包含时间信息，以便后续查询。")
    return prompt

@mcp.tool()
async def redis_put(ctx: Context,
                    usr_id: str,
                    key: str,
                    val: str,
                    ttl_s: int = 604800):
    """
    向Redis数据库存储一个键值对，用于持久化保存需要跨对话保留的信息或用户指定记录的数据。
    该工具会自动为键添加用户ID前缀，避免不同用户间的键名冲突。存储的数据具有生存时间（TTL），过期后自动删除。
    Args:
        usr_id (str): 用户唯一标识
        key (str): 需要创建的键值对中的键，与usr_id组合后形成实际存储的键（格式为 "{usr_id}:{key}"）
        val (str): 需要创建的键值对中的值，可以是任意的字符串
        ttl_s (int): 数据的生存时间，单位为秒。参数缺省时，默认值为604800秒（即7天）。
               有效范围：5~2419200秒（28天）。若传入值超出此范围，工具会自动截断至边界值。
               生存时间之后，该键值对将自动丢弃，无法查询！因此需要尽可能准确设置ttl_s而不是直接使用默认值。
               例如：存储一个x天后的行程，生存时间应当大于(86400*x)秒（即x天）；
                    存储一个当天的备忘录，生存时间应小于172800秒（即2天）。
    Return:
        bool: 存储成功返回true，存储失败返回false
    """
    formatted_key = f"{usr_id}:{key}"
    if ttl_s < 5:
        ttl_s = 5
    elif ttl_s > 2419200:
        ttl_s = 2419200
    db = ctx.request_context.lifespan_context["db"]
    result = await db.set(formatted_key, val, ex=ttl_s)
    return result

@mcp.tool()
async def redis_get(ctx: Context,
                    usr_id: str,
                    keys: list[str]):
    """
    在Redis数据库中获取指定的键对应的值，用于读取持久化保存的数据和跨对话信息。
    建议调用前先获取Redis数据库中所有与当前用户相关的键列表，再调用此工具获取键对应的值
    Args:
        usr_id (str): 用户唯一标识
        keys (list[str]): 需要搜索的键名列表，可包含一个或多个键名
    Return:
        list[str]型，与输入键列表顺序一致的值列表
        对于存在的键，返回对应的字符串值；
        对于不存在的键，返回空字符串
    """
    db = ctx.request_context.lifespan_context["db"]
    results = []
    for key in keys:
        formatted_key = f"{usr_id}:{key}"
        result = await db.get(formatted_key)
        if result is None:
            result = ""
        results.append(result)
    return results

# @mcp.resource("resource://redis/kv/{usr_id}")
@mcp.tool()
async def redis_scan(ctx: Context,
                     usr_id: str):
    """
    获取Redis数据库中所有与当前用户相关的键列表
    Args:
        usr_id (str): 用户唯一标识
    Return:
        如果Redis数据库中存在与当前用户相关的键，返回这些键；
        如果不存在与当前用户相关的键，返回 None
    """
    db = ctx.request_context.lifespan_context["db"]
    formatted_result = []
    cursor, keys = await db.scan(cursor=0, match=f"{usr_id}*", count=100)
    formatted_result.extend(keys)
    while cursor!=0:
        cursor, keys = await db.scan(cursor=cursor, match=f"{usr_id}*", count=100)
        formatted_result.extend(keys)
    result = [s.removeprefix(f"{usr_id}:") for s in formatted_result]
    # result = await db.keys(f"{usr_id}*")
    return result

@mcp.tool()
async def get_time(accuracy: Literal["year", "month", "date", "hour", "minute", "second"] = "date"):
    """
    获取当前时间，可选择精确程度（精确到年、月、日、时、分、秒）。
    基于服务器本地时间，不包含时区信息
    当需要存储涉及相对时间表述（如“今天”、“明天”、“十天后”）的信息时，不应直接存储这些模糊描述，
    而应调用此工具获取当前时间并计算出具体时间后，用具体时间替代存储，以保证后续处理的准确性和一致性。
    Args:
        accuracy (str): 时间的精确程度，其值仅可为"year", "month", "date", "hour", "minute", "second"中的一个，
                        分别对应精确到年、月、日、时、分、秒，参数缺省时默认为"date"（即精确到日）
    Return:
        str型，当前本地时间的格式化字符串，具体格式由accuracy参数决定。
    """
    now = datetime.now()
    if accuracy == "year":
        formatted = now.strftime("%Y")
    elif accuracy == "month":
        formatted = now.strftime("%Y-%m")
    elif accuracy == "date":
        formatted = now.strftime("%Y-%m-%d")
    elif accuracy == "hour":
        formatted = now.strftime("%Y-%m-%d %H")
    elif accuracy == "minute":
        formatted = now.strftime("%Y-%m-%d %H:%M")
    else:
        formatted = now.strftime("%Y-%m-%d %H:%M:%S")
    return formatted

@mcp.tool()
async def simple_calculation(expression: str):
    """
    接收数学表达式进行简单计算，例如四则运算
    Args:
        expression (str): 需要计算的数学表达式，以字符串形式提供，例如“1+2”
    Return:
        如果表达式可被计算，返回计算结果；否则返回错误信息
    """
    result = simple_eval(expression)
    return result

@mcp.tool()
async def time_calculation_diff(time1: str,
                                time2: str):
    """
    计算两个时间点的差，两个时间参数的精度和格式必须相同，例如都精确到日。
    提供的时间格式必须为“YYYY”、"YYYY-MM"、"YYYY-MM-DD"、“YYYY-MM-DD HH”、"YYYY-MM-DD HH:MM"、"YYYY-MM-DD HH:MM:SS"中的一个，
        精度分别对应年、月、日、时、分、秒。
    例如，在计算键值生存时间等场景需要计算两个时间点的差，可以调用此工具。
    Args:
        time1 (str): 起始时间，格式必须为“YYYY”、"YYYY-MM"、"YYYY-MM-DD"、“YYYY-MM-DD HH”、"YYYY-MM-DD HH:MM"、"YYYY-MM-DD HH:MM:SS"中的一个，
                    精度分别对应年、月、日、时、分、秒
        time2 (str): 结束时间，格式必须为“YYYY”、"YYYY-MM"、"YYYY-MM-DD"、“YYYY-MM-DD HH”、"YYYY-MM-DD HH:MM"、"YYYY-MM-DD HH:MM:SS"中的一个，
                    精度分别对应年、月、日、时、分、秒
    Returns:
        返回从起始时间到结束时间经过的时间。
        若提供的参数精度为年、月、日，则返回值以天为单位；若提供的参数精度为时、分、秒，则返回值以秒为单位。
        若结束时间time2在起始时间time1之前，则返回值为负数。
        若time1和time2精度不同，或者格式不符合要求，则返回错误信息。
    """
    formate_second = r'^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]) ([01]\d|2[0-3]):[0-5]\d:[0-5]\d$'
    formate_minute = r'^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]) ([01]\d|2[0-3]):[0-5]\d$'
    formate_hour = r'^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]) ([01]\d|2[0-3])$'
    formate_day = r'^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$'
    formate_month = r'^\d{4}-(0[1-9]|1[0-2])$'
    formate_year = r'^\d{4}$'
    if re.fullmatch(formate_second, time1):
        # 精度为秒
        if not re.fullmatch(formate_second, time2):
            return "错误：提供的时间参数精度不一致"
        dt_time1 = datetime.strptime(time1, "%Y-%m-%d %H:%M:%S")
        dt_time2 = datetime.strptime(time2, "%Y-%m-%d %H:%M:%S")
        delta_d = (dt_time2 - dt_time1).days
        delta_s = (dt_time2 - dt_time1).seconds
        return f"{delta_d*86400+delta_s}秒"
    elif re.fullmatch(formate_minute, time1):
        # 精度为分
        if not re.fullmatch(formate_minute, time2):
            return "错误：提供的时间参数精度不一致"
        dt_time1 = datetime.strptime(time1, "%Y-%m-%d %H:%M")
        dt_time2 = datetime.strptime(time2, "%Y-%m-%d %H:%M")
        delta_d = (dt_time2 - dt_time1).days
        delta_s = (dt_time2 - dt_time1).seconds
        return f"{delta_d*86400+delta_s}秒"
    elif re.fullmatch(formate_hour, time1):
        # 精度为时
        if not re.fullmatch(formate_hour, time2):
            return "错误：提供的时间参数精度不一致"
        dt_time1 = datetime.strptime(time1, "%Y-%m-%d %H")
        dt_time2 = datetime.strptime(time2, "%Y-%m-%d %H")
        delta_d = (dt_time2 - dt_time1).days
        delta_s = (dt_time2 - dt_time1).seconds
        return f"{delta_d*86400+delta_s}秒"
    elif re.fullmatch(formate_day, time1):
        # 精度为天
        if not re.fullmatch(formate_day, time2):
            return "错误：提供的时间参数精度不一致"
        dt_time1 = datetime.strptime(time1, "%Y-%m-%d")
        dt_time2 = datetime.strptime(time2, "%Y-%m-%d")
        delta_d = (dt_time2 - dt_time1).days
        return f"{delta_d}天"
    elif re.fullmatch(formate_month, time1):
        # 精度为月
        if not re.fullmatch(formate_month, time2):
            return "错误：提供的时间参数精度不一致"
        dt_time1 = datetime.strptime(time1, "%Y-%m")
        dt_time2 = datetime.strptime(time2, "%Y-%m")
        delta_d = (dt_time2 - dt_time1).days
        return f"{delta_d}天"
    elif re.fullmatch(formate_year, time1):
        # 精度为年
        if not re.fullmatch(formate_year, time2):
            return "错误：提供的时间参数精度不一致"
        dt_time1 = datetime.strptime(time1, "%Y")
        dt_time2 = datetime.strptime(time2, "%Y")
        delta_d = (dt_time2 - dt_time1).days
        return f"{delta_d}天"
    else:
        return "错误：提供的时间格式不符合要求"

@mcp.tool(tags={'debug'})
async def redis_scanAll(ctx: Context):
    """
    测试用，大模型不要调用
    列出Redis数据库中所有的键
    """
    db = ctx.request_context.lifespan_context["db"]
    result = await db.keys("*")
    return result

@mcp.tool(tags={'debug'})
async def redis_delete(ctx: Context,
                       usr_id: str,
                       key: str | None = None):
    """
    测试用，大模型不要调用
    删除指定键值对，或删除某用户的所有键值对
    """
    db = ctx.request_context.lifespan_context["db"]
    if key:
        formated_key = f"{usr_id}:{key}"
        result = await db.delete(formated_key)
    else:
        keys = await db.keys(f"{usr_id}:*")
        if keys:
            await db.delete(*keys)
        result = str(len(keys))
    return result

if __name__=="__main__":
    mcp.run(transport="streamable-http",
            host="0.0.0.0",
            port=8000)