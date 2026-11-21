"""Database engine + session helpers (SQLite).

Replaces Reflex's rx.session() usage with a plain SQLAlchemy session.
SQLite keeps the app self-contained (no external Postgres needed).
"""
import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base

# DB path: env override, else a file next to the project (persists across reloads).
DB_PATH = os.environ.get("TAILADMIN_DB", os.path.join(os.path.dirname(__file__), "..", "tailadmin.db"))
DB_URL = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.abspath(DB_PATH)}")

# check_same_thread=False so the pooled connection can serve NiceGUI's threads.
engine = create_engine(
    DB_URL,
    connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {},
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)


def init_db() -> None:
    """Create tables if they don't exist (idempotent)."""
    Base.metadata.create_all(engine)


@contextmanager
def session():
    """Transactional session context manager (commit on success, rollback on error)."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()