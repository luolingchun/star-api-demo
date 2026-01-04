from pydantic import BaseModel, Field
from star_openapi import UploadFile


class UploadFileForm(BaseModel):
    file: UploadFile
    file_type: str = Field(None, description="文件类型")


class DownloadFileQuery(BaseModel):
    filename: str = Field(None, description="文件名称")
