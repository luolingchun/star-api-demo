from rq import Queue

from app.config import REDIS_CONNECT

default_queue: Queue | None = None


def init_queue():
    global default_queue
    default_queue = Queue(name="default", connection=REDIS_CONNECT)
