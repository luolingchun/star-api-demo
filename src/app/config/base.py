# APP基础配置
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


# HTTP Basic
BASIC = [{"basic": []}]
BASIC_AUTH_USERNAME = "admin"
BASIC_AUTH_PASSWORD = "admin123"


# JWT
JWT = [{"jwt": []}]
JWT_SECRET_KEY = "hard to guess"
JWT_ACCESS_TOKEN_EXPIRE_SECONDS = 1 * 3600
JWT_REFRESH_TOKEN_EXPIRE_SECONDS = 7 * 24 * 3600
