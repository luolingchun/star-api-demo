import asyncio
import os

import uvicorn
from sqlalchemy import select
from starlette.responses import RedirectResponse

from app import create_app
from app.model.database import db

app = create_app()


@app.route("/")
def index(_):
    """根目录重定向到openapi"""
    return RedirectResponse(url="/openapi/swagger")


@app.cli.command("drop_alembic_version")
def drop_alembic_version():
    """删除 alembic_version 表"""

    async def _drop_alembic_version():
        from sqlalchemy import text
        from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

        from app.config import DB_URI, PG_PASSWORD, PG_URL, PG_USER

        # 默认数据库
        default_engine = create_async_engine(DB_URI, isolation_level="AUTOCOMMIT")
        default_session = async_sessionmaker(bind=default_engine, autoflush=False, expire_on_commit=False)
        async with default_session() as session:
            await session.execute(text("DROP TABLE IF EXISTS alembic_version"))
            await session.commit()
        # test 数据库
        test_engine = create_async_engine(
            f"postgresql+asyncpg://{PG_USER}:{PG_PASSWORD}@{PG_URL}/test", isolation_level="AUTOCOMMIT"
        )
        test_session = async_sessionmaker(bind=test_engine, autoflush=False, expire_on_commit=False)
        async with test_session() as session:
            await session.execute(text("DROP TABLE IF EXISTS alembic_version"))
            await session.commit()

    asyncio.run(_drop_alembic_version())


@app.cli.command("create_db")
def create_db():
    """创建数据库"""

    async def _create_db():
        from sqlalchemy import text
        from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

        from app.config import DB_URI, PG_PASSWORD, PG_URL, PG_USER

        # 创建 engine 和 sessionmaker
        default_engine = create_async_engine(DB_URI, isolation_level="AUTOCOMMIT")
        default_session = async_sessionmaker(bind=default_engine, autoflush=False, expire_on_commit=False)

        # 创建 test 数据库
        async with default_session() as session:
            db_is_exists_sql = text("SELECT u.datname  FROM pg_catalog.pg_database u where u.datname='test';")
            result = await session.execute(db_is_exists_sql)
            if result.scalar() is None:
                await session.execute(text("CREATE DATABASE test;"))
                print("create db test success.")
            else:
                print("db test exists.")
        # 创建扩展
        test_engine = create_async_engine(
            f"postgresql+asyncpg://{PG_USER}:{PG_PASSWORD}@{PG_URL}/test", isolation_level="AUTOCOMMIT"
        )
        test_session = async_sessionmaker(bind=test_engine, autoflush=False, expire_on_commit=False)
        async with test_session() as session:
            await session.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
            print("create db test extension postgis success.")
            await session.execute(text("CREATE EXTENSION IF NOT EXISTS postgis_topology;"))
            print("create db test extension postgis_topology success.")

    asyncio.run(_create_db())


@app.cli.command("init_db")
def init_db():
    """初始化数据库"""

    async def _init_db():
        from app.model.user import Role, User

        result = await db.session.execute(select(User).where(User.username == "super"))
        user = result.scalar()
        if user:
            print("超级管理员已存在.")
        else:
            user = User()
            user.username = "super"
            user.password = "123456"
            user.is_super = True
            user.is_active = True
            db.session.add(user)
            await db.session.commit()
            print("添加超级管理员成功.")
        await db.session.close()
        result = await db.session.execute(select(Role).where(Role.name == "普通用户"))
        role = result.scalar()
        if role:
            print("普通用户角色已存在.")
        else:
            role = Role()
            role.name = "普通用户"
            role.describe = "默认权限组"
            db.session.add(role)
            await db.session.commit()
            print("添加普通用户角色成功.")
        await db.session.close()

    asyncio.run(_init_db())


@app.cli.command("register_permission")
def register_permission():
    """注册权限"""

    async def _register_permission():
        from app.model.database import db
        from app.model.user import Permission
        from app.utils.jwt_tools import permissions

        for name, module, uuid in permissions:
            result = await db.session.execute(select(Permission).where(Permission.name == name))
            permission = result.scalar()
            if permission:
                print(f"{permission} is exists.")
                continue

            permission = Permission()
            permission.name = name
            permission.module = module
            permission.uuid = uuid
            db.session.add(permission)
            await db.session.commit()
            print(f"{name} register success.")
        await db.session.close()

    asyncio.run(_register_permission())


if __name__ == "__main__":
    uvicorn.run(
        "asgi:app",
        host="0.0.0.0",
        port=int(os.getenv("SERVER_PORT", "8000")),
        reload=os.getenv("DEBUG", "false").lower() == "true",
        # 工作进程数
        # workers=int(os.getenv("CPU", 0)) or os.cpu_count(),
        workers=1,
        loop="asyncio",
        http="httptools",
        # 限制并发请求数
        limit_concurrency=2000,
    )
