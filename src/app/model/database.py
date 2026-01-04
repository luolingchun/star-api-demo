import math
from contextvars import ContextVar

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.config import SQLALCHEMY_DATABASE_URI
from app.utils.exceptions import ResourceExistException

# 创建 engine 和 sessionmaker
engine = create_async_engine(SQLALCHEMY_DATABASE_URI)
async_session = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


# ContextVar 存储当前 session
_db_session_ctx: ContextVar[AsyncSession | None] = ContextVar("_db_session_ctx", default=None)


class DB:
    @property
    def session(self) -> AsyncSession:
        # 创建 session
        session = _db_session_ctx.get()
        if session is None:
            session = async_session()
            _db_session_ctx.set(session)
        return session

    @staticmethod
    async def close_db():
        """
        关闭当前请求的 session（如果存在）
        """
        session = _db_session_ctx.get()
        if session is not None:
            await session.close()
            _db_session_ctx.set(None)


db = DB()


# 中间件：请求结束统一关闭 session
class DBSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
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
