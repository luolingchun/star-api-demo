import os

from redis import Redis

REDIS_URL = os.getenv("REDIS_URL", "172.17.0.0.1:20263")
REDIS_USER = os.getenv("REDIS_USER", "redis_user")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "redis_password")
RQ_REDIS_URL = f"redis://{REDIS_URL}/0"
REDIS_CONNECT = Redis.from_url(RQ_REDIS_URL)
