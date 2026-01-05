set -ex
cd /work/src
star create_db
star drop_alembic_version && rm -rf /work/src/migrations/versions/*
cd /work/src/migrations
alembic revision --autogenerate
alembic upgrade head
cd cd /work/src
star init_db
star register_permission