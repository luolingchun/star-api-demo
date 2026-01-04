from pydantic import BaseModel, Field
from star_openapi import UploadFile


class PageModel(BaseModel):
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(15, ge=1, description="每页个数")


class IdModel(BaseModel):
    id: int = Field(..., description="ID")


class IdStringModel(BaseModel):
    id: str = Field(..., description="字符串ID")


class NameModel(BaseModel):
    name: str = Field(..., description="名称")


class FileModel(BaseModel):
    file: UploadFile


class JsonResponse(BaseModel):
    code: int = Field(default=0, description="状态码")
    message: str = Field(default="ok", description="异常信息")
