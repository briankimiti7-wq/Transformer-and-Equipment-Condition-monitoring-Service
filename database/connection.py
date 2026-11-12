"""Short-lived sessions; never cache user data in a global session."""
from functools import lru_cache
from contextlib import contextmanager
from contextvars import ContextVar
_CURRENT_SESSION = ContextVar("tecm_transaction", default=None)
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from config.settings import database_url

@lru_cache(maxsize=4)
def engine_for(url):
    engine = create_engine(url, connect_args={'check_same_thread': False, 'timeout': 15} if url.startswith('sqlite') else {})
    if url.startswith('sqlite'):
        @event.listens_for(engine, 'connect')
        def configure(dbapi_connection, _):
            cursor = dbapi_connection.cursor()
            cursor.execute('PRAGMA foreign_keys=ON')
            cursor.execute('PRAGMA busy_timeout=15000')
            cursor.execute('PRAGMA journal_mode=WAL')
            cursor.close()
    return engine

def get_engine():
    return engine_for(database_url())

@contextmanager
def session_scope():
    current = _CURRENT_SESSION.get()
    if current is not None:
        yield current
        return
    with sessionmaker(get_engine(), expire_on_commit=False)() as session:
        with session.begin():
            token = _CURRENT_SESSION.set(session)
            try:
                yield session
            finally:
                _CURRENT_SESSION.reset(token)
