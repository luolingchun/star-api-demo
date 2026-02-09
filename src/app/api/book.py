from star_openapi import APIRouter, Tag

from app.config import API_PREFIX, BASIC, JWT
from app.schema.book import BookBody, BookQuery
from app.utils.enums import PermissionGroup
from app.utils.http_basicauth import basic_required
from app.utils.jwt_tools import role_required
from app.utils.response import response

__version__ = "/v1"
__module__ = "/book"
url_prefix = API_PREFIX + __version__ + __module__
tag = Tag(name="图书", description="图书管理")
api = APIRouter(url_prefix=url_prefix, tags=[tag], security=JWT)


@api.post("/")
@role_required(name="创建图书", module=PermissionGroup.BOOK, uuid="1e1cbdb2-6bdb-4091-91ec-5268fa8f2b73")
async def create_book(body: BookBody):
    """创建图书"""
    print(body.name)
    print(body.author)
    return response()


@api.get("/{id}", security=BASIC)
@basic_required
async def get_book(path: BookQuery):
    """查询图书"""
    print(path)
    return response(data=path.id)


@api.delete("/{id}")
async def delete_book(path: BookQuery):
    """删除图书"""
    print(f"delete {path.id}")
    return response()
