from pydantic import BaseModel, Field


class ModifyPasswordBody(BaseModel):
    old_password: str = Field(..., min_length=6, max_length=32, description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=32, description="新密码")
    confirm_password: str = Field(..., min_length=6, max_length=32, description="确认密码")


class LoginBody(BaseModel):
    username: str = Field(..., min_length=4, max_length=32, description="用户名")
    password: str = Field(..., min_length=6, description="密码")


class UpdateUserBody(BaseModel):
    username: str = Field("", min_length=4, max_length=32, description="用户名")
    fullname: str = Field("", min_length=2, max_length=32, description="姓名")
