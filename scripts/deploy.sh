set -ex
cd /work/src
star create_db
star drop_alembic_version && rm -rf /work/src/migrations/versions/*
alembic revision --autogenerate
alembic upgrade head
star init_db
star register_permission