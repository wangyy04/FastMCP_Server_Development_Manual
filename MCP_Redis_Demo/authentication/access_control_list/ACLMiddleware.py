"""
ACL中间件，实现对连接的客户端验证身份（使用ACL）
(1) 使用查询参数传递key
    采用此方法时，客户端需要连接形如"localhost:8000/mcp?key=c61f771c05682942a27a2571f3fb0aee"的URL，
    以此向服务器提供查询参数key，参数缺省则401 Unauthorized或未在服务器记录则403 Forbidden
(2) 使用HTTP Header传递key
    采用此方法时，客户端需要在Header中以形如"key=c61f771c05682942a27a2571f3fb0aee"的形式
    向服务器提供参数key，参数缺省则401 Unauthorized或未在服务器记录则403 Forbidden
"""
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.server.dependencies import get_http_request
import os
from pathlib import Path
from typing import Literal

class ACLMiddleware(Middleware):
    __key_fileName_set: set[str]    # 私钥文件名集合（文件名包含".pem"）
    __param_passing_method: Literal["query", "header"]  # 参数提供方式

    def __init__(self, directory: Path, method: Literal["query", "header"] = "query"):
        # 初始化时提供路径，将文件名加载入集合，以便后续快速查找；并设定参数提供方式
        self.__key_fileName_set = {entry.name for entry in os.scandir(directory) if entry.is_file()}
        self.__param_passing_method = method

    async def __call__(self, ctx: MiddlewareContext, call_next):
        request = get_http_request()
        public_token = None
        # 根据所选提供参数方式读取参数key
        if self.__param_passing_method == "query":
            public_token = request.query_params.get('key')
        elif self.__param_passing_method == "header":
            public_token = request.headers.get('key')

        # 若public_token为str则全转小写
        if isinstance(public_token, str):
            public_token = public_token.lower()

        if (public_token is None) or len(public_token)<=0:
            # 若未提供参数则返回401
            raise Exception("401 Unauthorized — Key Required")
        elif f"{public_token}.pem" in self.__key_fileName_set:
            # 提供key参数并且提供的公钥的MD5在集合内则正常提供服务
            pass
        else:
            # 身份验证未通过，返回403，拒绝服务
            raise Exception("403 Forbidden")
        return await call_next(ctx) # 继续后续程序