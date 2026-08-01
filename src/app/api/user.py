import jwt
from jwt import ExpiredSignatureError, PyJWTError
from sqlalchemy import select
from star_openapi import APIRouter, Tag
from starlette.requests import Request

from app.config import API_PREFIX, JWT, JWT_SECRET_KEY
from app.model.database import db
from app.model.user import Permission, User
from app.schema.user.user import LoginBody, ModifyPasswordBody
from app.utils.exceptions import ExpiredTokenException, InvalidTokenException, RefreshException, UserNotExistException
from app.utils.jwt_tools import get_token, login_required
from app.utils.response import response

__version__ = "/v1"
__module__ = "/user"
url_prefix = API_PREFIX + __version__ + __module__
tag = Tag(name="用户", description="用户注册、登录、个人管理")
api = APIRouter(url_prefix=url_prefix, tags=[tag], security=JWT)


@api.post("/login", summary="用户登录")
async def login(body: LoginBody):
    """用户登录"""
    user = await User.verify(body.username, body.password)
    access_token, refresh_token = get_token(user)
    return response(data={"access_token": access_token, "refresh_token": refresh_token})


@api.get("/info", summary="获取用户信息")
@login_required
async def get_info(request: Request):
    """获取用户信息"""
    user = request.state.user
    data = {
        "username": user.username,
        "email": user.email,
    }
    return response(data=data)


@api.put("/password", summary="修改密码")
@login_required
async def modify_password(request: Request, body: ModifyPasswordBody):
    """修改密码"""
    user = request.state.user
    await user.modify_password(body.old_password, body.new_password, body.confirm_password)
    return response()


@api.get("/permissions", summary="获取用户权限")
@login_required
async def get_permissions(request: Request):
    """获取用户拥有的权限"""
    user = request.state.user
    if user.is_super:
        result = await db.session.execute(select(Permission))
        permissions = result.scalars()
    else:
        roles = user.roles
        permissions = [permission for role in roles for permission in role.permissions]
    data = {}
    for permission in permissions:
        permission_data = permission.data()
        module = permission_data["module"]
        if not data.get(module):
            data[module] = []
            data[module].append(permission_data)
        else:
            data[module].append(permission_data)
    return response(data=data)


@api.get("/refresh", summary="刷新令牌")
async def refresh(request: Request):
    try:
        # 从Authorization header中获取token
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise RefreshException()

        token = auth_header.split(" ")[1]

        # 解码refresh token
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("id")

        if user_id is None:
            raise InvalidTokenException()

    except ExpiredSignatureError:
        raise ExpiredTokenException()
    except PyJWTError:
        raise InvalidTokenException()

    # 查询用户
    result = await db.session.execute(select(User).where(User.id == user_id))
    user = result.scalar()
    if user is None:
        raise UserNotExistException()

    # 生成新的访问令牌
    access_token, refresh_token = get_token(user)

    return response(data=access_token)
