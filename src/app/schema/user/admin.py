from pydantic import BaseModel, Field

from app.schema import PageModel


class AddUserBody(BaseModel):
    username: str = Field(..., min_length=4, max_length=32, description="用户名")
    fullname: str = Field(..., max_length=32, description="姓名")
    password: str = Field(..., min_length=6, max_length=32, description="密码")
    role_ids: list[int] = Field(..., description="角色ID列表")

    system: str = Field(..., description="系统")


class RoleBody(BaseModel):
    name: str = Field(..., max_length=32, description="名称")
    describe: str = Field(..., description="描述")
    menus: list[dict] = Field(..., description="菜单列表")
    permission_ids: list[int] = Field([], description="权限ID列表")
    system: str = Field(..., description="系统")


class RoleQuery(PageModel):
    name: str = Field("", description="名称")
    system: str = Field("", description="系统")


class ResetPassword(BaseModel):
    password: str = Field(..., min_length=6, max_length=32, description="密码")
    confirm_password: str = Field(..., min_length=6, max_length=32, description="确认密码")


class UpdateRoleBody(BaseModel):
    name: str = Field("", max_length=32, description="角色名称")
    describe: str = Field("", description="角色描述")
    system: str = Field("", description="系统")


class UserQuery(PageModel):
    username: str = Field("", description="用户名")
    role_id: int = Field(0, description="角色ID")
    is_active: str = Field("", description="是否激活")
    system: str = Field("", description="系统")


class UserRoleBody(BaseModel):
    user_id: int = Field(..., description="用户ID")
    role_ids: list[int] = Field([], description="角色ID列表")


class RolePermissionBody(BaseModel):
    role_id: int = Field(..., description="角色ID")
    menus: list[dict] = Field([], description="菜单列表")
    permission_ids: list[int] = Field([], description="权限ID列表")
