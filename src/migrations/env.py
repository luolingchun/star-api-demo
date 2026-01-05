import asyncio
from logging.config import fileConfig

from alembic import context
from geoalchemy2.alembic_helpers import render_item, writer

from app.model.database import sqlalchemy_engines
from migrations.alembic_helpers import include_object

# Alembic 配置
config = context.config
fileConfig(config.config_file_name)


def do_run_migrations(connection, metadata, engine_name=None):
    context.configure(
        connection=connection,
        target_metadata=metadata,
        upgrade_token="%s_upgrades" % engine_name,
        downgrade_token="%s_downgrades" % engine_name,
        compare_server_default=True,
        include_object=include_object,
        render_item=render_item,
        process_revision_directives=writer,
    )
    with context.begin_transaction():
        context.run_migrations(engine_name=engine_name)


async def run_migrations_online():
    for engine_name, value in sqlalchemy_engines.items():
        metadata = value["metadata"]
        engine = value["engine"]
        async with engine.connect() as connect:
            await connect.run_sync(do_run_migrations, metadata, engine_name)

        await engine.dispose()


asyncio.run(run_migrations_online())
