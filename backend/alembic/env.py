import sys
from os.path import abspath, dirname
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context


sys.path.insert(0, dirname(dirname(abspath(__file__))))


from database import Base
from models import *  

config = context.config
fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=True,
            include_schemas=True  
        )

        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()