import asyncio
from logging.config import fileConfig

from alembic import context
from geoalchemy2.alembic_helpers import render_item, writer
from sqlalchemy.ext.asyncio import create_async_engine

from app.config.postgres import SQLALCHEMY_BINDS, SQLALCHEMY_DATABASE_URI, SQLALCHEMY_ENGINE_OPTIONS
from app.model.base import DefaultBase, TestBase
from migrations.alembic_helpers import include_object

# Alembic 配置
config = context.config
fileConfig(config.config_file_name)


metadata_dict = {
    "default": DefaultBase.metadata,
    "test": TestBase.metadata,
}


def do_run_migrations(connection, metadata, bind_key=None):
    context.configure(
        connection=connection,
        target_metadata=metadata,
        upgrade_token="%s_upgrades" % bind_key,
        downgrade_token="%s_downgrades" % bind_key,
        compare_server_default=True,
        include_object=include_object,
        render_item=render_item,
        process_revision_directives=writer,
    )
    with context.begin_transaction():
        context.run_migrations(engine_name=bind_key)


async def run_migrations_online():
    for bind_key, metadata in metadata_dict.items():
        url = SQLALCHEMY_DATABASE_URI if bind_key == "default" else SQLALCHEMY_BINDS[bind_key]
        engine = create_async_engine(url, **SQLALCHEMY_ENGINE_OPTIONS)
        async with engine.connect() as connect:
            await connect.run_sync(do_run_migrations, metadata, bind_key)

        await engine.dispose()


asyncio.run(run_migrations_online())
