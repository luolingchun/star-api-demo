import os

from star_openapi import APIRouter, Tag
from starlette.responses import FileResponse, Response

from app.config import API_PREFIX, FILE_PATH
from app.schema import NameModel
from app.schema.file import UploadFileForm
from app.utils.exceptions import ResourceNotExistException
from app.utils.response import response

__version__ = "/v1"
__module__ = "/file"


url_prefix = API_PREFIX + __version__ + __module__
tag = Tag(name="文件", description="文件管理")
api = APIRouter(url_prefix=url_prefix, tags=[tag])


@api.post("/upload", summary="上传文件")
async def upload_file(form: UploadFileForm):
    """上传文件"""
    print(form.file.filename)
    print(form.file_type)
    content = await form.file.read()
    with open(form.file.filename, "wb") as f:
        f.write(content)
    return response()


@api.get("/", summary="下载文件")
async def download_file(query: NameModel):
    """下载文件"""
    file_path = os.path.join(FILE_PATH, query.filename)
    if os.path.exists(file_path):
        return FileResponse(path=file_path, filename=query.filename, media_type="application/octet-stream")
    raise ResourceNotExistException()


@api.get("/image", summary="获取图片流")
async def get_image(query: NameModel):
    file_path = os.path.join(FILE_PATH, query.filename)
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            content = f.read()
        return Response(content=content, media_type="image/jpeg")
    raise ResourceNotExistException()
