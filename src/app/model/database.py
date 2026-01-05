import math
from contextvars import ContextVar
from datetime import datetime

from sqlalchemy import DateTime, Integer, and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.config import (
    PG_PASSWORD,
    PG_URL,
    PG_USER,
    SQLALCHEMY_ENGINE_OPTIONS,
)
from app.utils.exceptions import ResourceExistException


class DefaultBase(DeclarativeBase):
    """基础数据库模型：提供id、创建时间、更新时间"""

    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="主键")
    create_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")
    update_time: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )


class TestBase(DeclarativeBase):
    """test 数据库基础模型"""

    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="主键")
    create_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")
    update_time: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )


# 多数据库定义
sqlalchemy_engines = {
    "default": {
        "engine": create_async_engine(
            f"postgresql+asyncpg://{PG_USER}:{PG_PASSWORD}@{PG_URL}/star", **SQLALCHEMY_ENGINE_OPTIONS
        ),
        "metadata": DefaultBase.metadata,
    },
    "test": {
        "engine": create_async_engine(
            f"postgresql+asyncpg://{PG_USER}:{PG_PASSWORD}@{PG_URL}/test", **SQLALCHEMY_ENGINE_OPTIONS
        ),
        "metadata": TestBase.metadata,
    },
}


# 多数据库引擎
sqlalchemy_sessions = {
    "default": async_sessionmaker(
        bind=sqlalchemy_engines["default"]["engine"],
        autoflush=False,
        expire_on_commit=False,
    ),
    "test": async_sessionmaker(
        bind=sqlalchemy_engines["test"]["engine"],
        autoflush=False,
        expire_on_commit=False,
    ),
}


# ContextVar 存储当前 session
_db_session_ctx: ContextVar[AsyncSession | None] = ContextVar("_db_session_ctx", default=None)


class DB:
    @property
    def session(self) -> AsyncSession:
        return self.get_session()

    @staticmethod
    def get_session(engine="default") -> AsyncSession:
        # 创建 session
        session = _db_session_ctx.get()
        if session is None:
            session = sqlalchemy_sessions.get(engine, sqlalchemy_sessions["default"])()
            _db_session_ctx.set(session)
        return session

    @staticmethod
    async def close_db():
        # 关闭当前请求的 session（如果存在）
        session = _db_session_ctx.get()
        if session is not None:
            await session.close()
            _db_session_ctx.set(None)


db = DB()


class DBSessionMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        try:
            await self.app(scope, receive, send)
        finally:
            await db.close_db()


def get_offset_limit(page, page_size):
    """获取页码偏移量"""
    page = 1 if page < 1 else page
    limit = page_size
    offset = (page - 1) * limit
    return offset, limit


async def get_total_page(_id, condition, limit):
    """获取总个数、总页数"""
    result = await db.session.execute(select(func.count(_id)).where(*condition))
    total = result.scalar()
    total_page = math.ceil(total / limit)
    return total, total_page


async def validate_name(model, key, value, message="名称"):
    # 高并发场景下会失效
    result = await db.session.execute(select(model).where(and_(key == value)))
    if result.first():
        raise ResourceExistException(message=f"{message}已存在")


async def validate_name_when_update(model, model_id, key, value, message="名称"):
    # 高并发场景下会失效
    result = await db.session.execute(select(model).where(and_(model.user_id != model_id, key == value)))
    if result.scalar():
        raise ResourceExistException(message=f"{message}已存在")
