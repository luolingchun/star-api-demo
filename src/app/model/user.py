r"""
采用经典的权限五表设计：
User        Role        Permission
  \         /   \        /
   \       /     \      /
    uer_role     role_permission
User和Role为多对多关系
Role和Permission为多对多关系
"""

from passlib.hash import sha256_crypt
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, select
from sqlalchemy.orm import Mapped, relationship

from app.schema.user.admin import AddUserBody, UpdateRoleBody
from app.schema.user.user import UpdateUserBody
from app.utils.exceptions import ActiveException, PasswordException, UserNotExistException

from . import db
from .database import DefaultBase

UserRole = Table(
    "user_role",
    DefaultBase.metadata,
    Column("user_id", Integer, ForeignKey("user.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("role.id"), primary_key=True),
)

RolePermission = Table(
    "role_permission",
    DefaultBase.metadata,
    Column("role_id", Integer, ForeignKey("role.id")),
    Column("permission_id", Integer, ForeignKey("permission.id")),
)


class User(DefaultBase):
    __tablename__ = "user"
    __table_args__ = {"comment": "用户表"}
    username: Mapped[str] = Column(String(32), unique=True, nullable=False, comment="用户名")
    fullname: Mapped[str] = Column(String(32), unique=False, nullable=False, default="", comment="姓名")
    _password = Column("password", String(1024), comment="密码")

    is_super: Mapped[bool] = Column(Boolean, unique=False, nullable=False, default=False, comment="是否是超级管理员")
    is_active: Mapped[bool] = Column(Boolean, unique=False, nullable=False, default=False, comment="是否激活")

    roles = relationship("Role", secondary=UserRole, back_populates="users", lazy="selectin")

    system = Column(String(100), comment="系统")

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, raw):
        self._password = sha256_crypt.hash(raw)

    def check_password(self, raw):
        if not self._password:
            return False
        return sha256_crypt.verify(raw, self._password)

    async def modify_password(self, session, old_password=None, new_password=None, confirm_password=None, admin=False):
        if new_password != confirm_password:
            raise PasswordException(message="密码不一致")
        if admin:
            self.password = new_password
            await session.commit()
            return
        if self.check_password(old_password):
            self.password = new_password
            await session.commit()
        else:
            raise PasswordException(message="原始密码错误")

    @staticmethod
    async def create(body: AddUserBody):
        user = User()
        user.username = body.username
        user.fullname = body.fullname
        user.password = body.password
        user.system = body.system

        # 用户注册后自动激活
        user.is_active = True

        role_ids = body.role_ids
        if not role_ids:
            # 默认位普通用户
            role_ids = [1]
        # 添加角色
        result = await db.session.execute(select(Role).where(Role.id.in_(role_ids)))
        user.roles = result.scalars().all()

        await db.session.add(user)
        await db.session.commit()

        return user

    async def update_info(self, body: UpdateUserBody):
        if self.is_super:
            return None
        if body.username:
            self.username = body.username
        self.fullname = body.fullname

        await db.session.commit()

        return True

    def brief_data(self):
        return {
            "username": self.username,
            "fullname": self.fullname,
            "role": [role.name for role in self.roles],
        }

    def data(self):
        data = {
            "id": self.id,
            "username": self.username,
            "fullname": self.fullname,
            "is_active": self.is_active,
            "roles": [role.data() for role in self.roles],
        }

        return data

    @classmethod
    async def verify(cls, username, password):
        """验证用户名密码"""
        result = await db.session.execute(select(cls).where(cls.username == username))
        user = result.scalar()
        if user is None:
            raise UserNotExistException()
        if not user.check_password(password):
            raise PasswordException()
        if not user.is_active:
            raise ActiveException()
        return user


class Role(DefaultBase):
    __tablename__ = "role"
    __table_args__ = {"comment": "角色表"}
    name: Mapped[str] = Column(String(32), unique=True, comment="角色名称")
    describe = Column(String(255), comment="角色描述")

    users = relationship("User", secondary=UserRole, back_populates="roles", lazy="selectin")
    permissions = relationship("Permission", secondary=RolePermission, back_populates="roles", lazy="selectin")

    @staticmethod
    async def create(name, describe, permission_ids):
        role = Role()
        role.name = name
        role.describe = describe

        if permission_ids:
            result = await db.session.execute(select(Permission).where(Permission.id.in_(permission_ids)))
            role.permissions = result.scalars().all()
        await db.session.add(role)
        await db.session.commit()

    async def update(self, body: UpdateRoleBody):
        self.name = body.name
        self.describe = body.describe
        await db.session.commit()

    def data(self):
        return {
            "id": self.id,
            "name": self.name,
            "describe": self.describe,
            "permissions": [permission.data() for permission in self.permissions],
        }

    def brief_data(self):
        return {
            "id": self.id,
            "name": self.name,
        }


class Permission(DefaultBase):
    __tablename__ = "permission"
    __table_args__ = {"comment": "权限表"}
    name = Column(String(32), unique=True, comment="权限名称")
    module = Column(String(32), comment="权限模块")
    uuid = Column(String(255), unique=True, comment="权限uuid")

    roles = relationship("Role", secondary=RolePermission, back_populates="permissions")

    def __repr__(self):
        return f"{self.name}-{self.uuid}"

    def data(self):
        return {"id": self.id, "name": self.name, "module": self.module}
