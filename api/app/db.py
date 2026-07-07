"""Database engine + session management (SQLite via SQLModel)."""

from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import event
from sqlmodel import Session, SQLModel, create_engine

from .config import settings

# check_same_thread=False lets FastAPI's threadpool share the SQLite connection.
engine = create_engine(
    settings.database_url,
    echo=False,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
)


@event.listens_for(engine, "connect")
def _enable_sqlite_fks(dbapi_connection, _record):  # pragma: no cover - driver glue
    """SQLite ignores foreign keys (and cascades) unless asked per-connection."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def init_db() -> None:
    """Create tables. Import models first so they register on SQLModel.metadata."""
    from . import models  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
