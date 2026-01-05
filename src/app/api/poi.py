from sqlalchemy import select
from star_openapi import APIRouter, Tag

from app.config import API_PREFIX, JWT
from app.model.database import db, get_offset_limit, get_total_page
from app.model.poi import POI
from app.schema import PageModel
from app.schema.poi import CreatePOIBody
from app.utils.exceptions import ResourceExistException
from app.utils.response import response

__version__ = "/v1"
__module__ = "/poi"
url_prefix = API_PREFIX + __version__ + __module__
tag = Tag(name="地名", description="地名管理")
api = APIRouter(url_prefix=url_prefix, tags=[tag], security=JWT)


@api.post("/", summary="创建地名")
async def create_book(body: CreatePOIBody):
    result = await db.get_session("test").execute(select(POI).where(POI.name == body.name))
    poi = result.scalar()
    if poi:
        raise ResourceExistException()
    await POI.create(body)
    return response()


@api.get("/", summary="获取地名数据列表")
async def get_poi(query: PageModel):
    offset, limit = get_offset_limit(query.page, query.page_size)
    result = await db.get_session("test").execute(select(POI).order_by(POI.id.desc()).offset(offset).limit(limit))
    poi_list = result.scalars()
    total, total_page = await get_total_page(POI.id, [], limit)
    data = [poi.data() for poi in poi_list]
    return response(data=data, total=total, total_page=total_page)
