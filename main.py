import os
from pathlib import Path

from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import scoped_session, sessionmaker


BASE_DIR = Path('../').absolute()

engine = create_engine(f"sqlite:///{BASE_DIR}/db.sqlite3", echo=False)

session = scoped_session(
    sessionmaker(
        autoflush = False,
        autocommit = False,
        bind=engine
    )
)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()