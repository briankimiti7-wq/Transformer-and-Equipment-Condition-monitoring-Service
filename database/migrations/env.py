from alembic import context
from database.connection import get_engine
from database.models import Base

config = context.config

def run():
    if context.is_offline_mode():
        from config.settings import database_url
        context.configure(url=database_url(), target_metadata=Base.metadata, literal_binds=True, render_as_batch=True)
        with context.begin_transaction():
            context.run_migrations()
    else:
        with get_engine().connect() as connection:
            context.configure(connection=connection, target_metadata=Base.metadata, render_as_batch=True, compare_type=True)
            with context.begin_transaction():
                context.run_migrations()
run()
