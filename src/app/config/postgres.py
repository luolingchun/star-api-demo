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
# 多数据库
SQLALCHEMY_BINDS = {
    "test": f"postgresql+asyncpg://{PG_USER}:{PG_PASSWORD}@{PG_URL}/test",
}
SQLALCHEMY_ENGINE_OPTIONS = {
    # 全局写入json时的序列化操作
    "json_serializer": lambda obj: json.dumps(obj, ensure_ascii=False)
}
