import json
import os

# 数据库配置：sqlite
SQLITE_DB_URI = "sqlite:///../star_api.db"
# 数据库配置：postgres
PG_USER = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "123456")
PG_DB = os.getenv("PG_DB", "star")
PG_URL = os.getenv("PG_URL", "star-api-demo-postgres:5432")
DB_URI = f"postgresql+asyncpg://{PG_USER}:{PG_PASSWORD}@{PG_URL}/{PG_DB}"
if not bool(int(os.getenv("DEV", 0))):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
# SQLALCHEMY_DATABASE_URI = SQLITE_DB_URI
SQLALCHEMY_DATABASE_URI = DB_URI


SQLALCHEMY_ENGINE_OPTIONS = {
    # 全局写入json时的序列化操作
    "json_serializer": lambda obj: json.dumps(obj, ensure_ascii=False),
    # 连接池中的连接数量
    "pool_size": 20,
    # 连接池外允许的最大连接数
    "max_overflow": 30,
    # 启用连接预检查
    "pool_pre_ping": True,
    "pool_timeout": 30,
    # 连接回收时间（秒）
    "pool_recycle": 3600,
}
