from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import DefaultBase


class Book(DefaultBase):
    __tablename__ = "book"
    __table_args__ = {"comment": "图书表"}
    name: Mapped[str] = mapped_column(String(32), comment="名称")
    author: Mapped[str] = mapped_column(String(4), comment="作者")
