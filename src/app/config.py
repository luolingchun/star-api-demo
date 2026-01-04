import json
import os

from redis import Redis

# -------------------APP基础配置-------------------
APP_NAME = "Star OpenAPI"
APP_VERSION = "1.0.0"
API_PREFIX = "/api"
# Swagger UI 配置项：https://github.com/swagger-api/swagger-ui/blob/master/docs/usage/configuration.md
SWAGGER_CONFIG = {
    "docExpansion": "none",
    "validatorUrl": None,
    "tryItOutEnabled": True,
    "filter": True,
    "tagsSorter": "alpha",
    "persistAuthorization": True,
}
# -------------------APP基础配置-------------------


# -------------------redis数据库配置-------------------
REDIS_HOST = os.getenv("REDIS_HOST", "star-redis")
REDIS_USER = os.getenv("REDIS_USER", "redis_user")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "redis_password")
REDIS_PORT = 6379
RQ_REDIS_DB = 0
RQ_REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{RQ_REDIS_DB}"
REDIS_CONNECT = Redis.from_url(RQ_REDIS_URL)
# -------------------redis数据库配置-------------------
