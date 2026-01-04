import time
from functools import wraps

import jwt
from jwt import ExpiredSignatureError, PyJWTError
from sqlalchemy import select
from starlette.requests import Request

from app.config import JWT_ACCESS_TOKEN_EXPIRE_SECONDS, JWT_REFRESH_TOKEN_EXPIRE_SECONDS, JWT_SECRET_KEY
from app.model.database import db
from app.model.user import User
from app.utils.exceptions import (
    ActiveException,
    ExpiredTokenException,
    InvalidTokenException,
    PermissionException,
    UserNotExistException,
)

# 存放所有权限，数据库初始化时使用
permissions = []


def role_required(name, module, uuid):
    """
    装饰器工厂函数
    :param name: 权限名称
    :param module: 权限模块
    :param uuid: 唯一ID
    :return: decorator
    """

    def decorator(func):
        """装饰器，为func添加权限属性"""
        global permissions
        permissions.append([name, module, uuid])
        setattr(func, "uuid", uuid)

        @wraps(func)
        async def wrapper(request, *args, **kwargs):
            user = await get_current_user(request)

            if await is_user_allowed(user, func.uuid):
                return await func(*args, **kwargs)
            else:
                raise PermissionException(message="权限不足")

        return wrapper

    return decorator


def download_required(name, module, uuid):
    """
    装饰器工厂函数
    :param name: 权限名称
    :param module: 权限模块
    :param uuid: 唯一ID
    :return: decorator
    """

    def decorator(func):
        """装饰器，为func添加权限属性"""
        global permissions
        permissions.append([name, module, uuid])
        setattr(func, "uuid", uuid)

        @wraps(func)
        async def wrapper(request, *args, **kwargs):
            # 从查询参数中获取token
            token = request.query_params.get("token") if request else None
            if not token:
                raise PermissionException(message="缺少访问令牌")

            # 验证token
            try:
                payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
                user_id = payload.get("id")
                if user_id is None:
                    raise InvalidTokenException()
            except jwt.PyJWTError:
                raise InvalidTokenException()

            # 获取用户
            user = await db.session.execute(select(User).where(User.id == user_id))
            user = user.scalar()
            if user is None:
                raise UserNotExistException()

            if await is_user_allowed(user, func.uuid):
                return await func(*args, **kwargs)
            else:
                raise PermissionException(message="权限不足")

        return wrapper

    return decorator


def login_required(func):
    """登录装饰器"""

    @wraps(func)
    async def wrapper(request, *args, **kwargs):
        user = await get_current_user(request)
        if not user.is_active:
            raise ActiveException()
        return await func(*args, **kwargs)

    return wrapper


def is_super(func):
    """判断是否是超级管理员"""

    @wraps(func)
    async def wrapper(request, *args, **kwargs):
        user = await get_current_user(request)
        if not user.is_super:
            raise PermissionException(message="权限不足")
        return await func(*args, **kwargs)

    return wrapper


async def get_current_user(request: Request):
    """获取当前用户"""
    try:
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            raise PermissionException()

        token = auth.split(" ")[1]
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("id")
        if user_id is None:
            raise InvalidTokenException()
    except ExpiredSignatureError:
        raise ExpiredTokenException()
    except PyJWTError:
        raise InvalidTokenException()

    result = await db.session.execute(select(User).where(User.id == user_id))
    user: User = result.scalar()
    if user is None:
        raise UserNotExistException()
    return user


def get_token(user):
    """生成访问令牌和刷新令牌"""
    # 创建访问令牌
    access_expire = int(time.time()) + JWT_ACCESS_TOKEN_EXPIRE_SECONDS
    access_payload = {"id": user.id, "exp": access_expire}
    access_token = jwt.encode(access_payload, JWT_SECRET_KEY, algorithm="HS256")

    # 创建刷新令牌
    refresh_expire = int(time.time()) + JWT_REFRESH_TOKEN_EXPIRE_SECONDS
    refresh_payload = {"id": user.id, "exp": refresh_expire}
    refresh_token = jwt.encode(refresh_payload, JWT_SECRET_KEY, algorithm="HS256")

    return access_token, refresh_token


async def is_user_allowed(user, uuid):
    """判断用户是否有权限"""
    if user.is_super:
        return True
    roles = user.roles
    uuid_list = []
    for role in roles:
        for p in role.permissions:
            uuid_list.append(p.uuid)

    return uuid in uuid_list
