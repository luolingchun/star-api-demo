#!/bin/bash
cd /work/src

SERVER_WORKERS=${SERVER_WORKERS:-4}

exec uvicorn asgi:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers SERVER_WORKERS \
    --loop asyncio \
    --http httptools \
    --limit-concurrency 2000
