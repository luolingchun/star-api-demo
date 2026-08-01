import importlib
import os
import traceback

from star_openapi import Info, OpenAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app.model.database import DBSessionMiddleware
from app.utils.exceptions import BaseAPIException


def init_exception(app: OpenAPI):
    def exception_handler(_request, exc):
        if isinstance(exc, BaseAPIException):
            return exc.response()
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "code": -1,
                    "message": "服务器未知错误",
                },
            )

    app.add_exception_handler(BaseAPIException, exception_handler)


def auto_register_api(app: OpenAPI):
    """自动注册蓝图API
    自动寻找api文件夹中的APIBlueprint并完成注册
    """
    here = os.path.dirname(__file__)
    api_dir = os.path.join(here, "api")
    for root, dirs, files in os.walk(api_dir):
        for file in files:
            if file.startswith("__init__"):
                continue
            if not file.endswith(".py") and not file.endswith(".pyd") and not file.endswith(".so"):
                continue
            api_file = os.path.join(root, file)
            api_route = "app" + api_file.split(".")[0].split("app")[1].replace(os.sep, ".")
            # noinspection PyBroadException
            try:
                api = importlib.import_module(api_route)
                app.register_api(api.api)
            except AttributeError:
                print(f"模块 {api_route} 中没有api变量")
            except Exception:
                traceback.print_exc()
                print(f"模块 {api_route} 自动注册错误")


def register_apis(app: OpenAPI):
    """注册API蓝图"""
    # from app.api.user import api as user_api
    # from app.api.admin import api as admin_api
    # from app.api.book import api as book_api
    # from app.api.file import api as file_api
    # from app.api.job import api as job_api
    # app.register_api(user_api)
    # app.register_api(admin_api)
    # app.register_api(book_api)
    # app.register_api(file_api)
    # app.register_api(job_api)
    auto_register_api(app)


def init_rq():
    """初始化rq2"""
    from app.rq import init_queue

    init_queue()


def create_app():
    from . import config

    # 创建APP实例
    app = OpenAPI(
        info=Info(title=config.APP_NAME, version=config.APP_VERSION),
        security_schemes={
            "basic": {"type": "http", "scheme": "basic"},
            "jwt": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"},
        },
    )
    # 使用真实IP
    app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")
    # 全局配置项
    app.config.from_object(config)
    # 初始化全局异常
    init_exception(app)
    # 跨域支持
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 允许的源
        allow_credentials=True,
        allow_methods=["*"],  # GET, POST, PUT, DELETE ...
        allow_headers=["*"],  # Authorization, Content-Type ...
    )
    # 数据库session中间件
    app.add_middleware(DBSessionMiddleware)
    # 初始化rq
    init_rq()
    # 注册API蓝图
    register_apis(app)
    return app
