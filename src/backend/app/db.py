"""Database engine and session dependency.

The SQLite file lives at ``src/backend/data/cph.db`` (resolved from this file, not the
current working directory). Override it with the ``CPH_DB_PATH`` environment variable,
which the tests use to work on a throwaway database. An optional ``.env`` file in the
repository root is loaded first, so the app, the seed script and ``check_env.py`` all
see the same settings (real environment variables win).
"""

import os
from collections.abc import Iterator
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import inspect
from sqlmodel import Session, SQLModel, create_engine, select

BACKEND_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BACKEND_DIR.parent.parent
load_dotenv(REPO_ROOT / ".env")

DEFAULT_DB_PATH = BACKEND_DIR / "data" / "cph.db"
DB_PATH = Path(os.environ.get("CPH_DB_PATH") or DEFAULT_DB_PATH)

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},  # FastAPI may use the session from another thread
)


def create_db_and_tables() -> None:
    """Create all tables that don't exist yet (safe to call on every start-up)."""
    from backend.app import models  # noqa: F401  (registers the tables on SQLModel.metadata)

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    """FastAPI dependency that yields one database session per request."""
    with Session(engine) as session:
        yield session


def db_has_data() -> bool:
    """Return True when the database exists and has been seeded (airports present)."""
    from backend.app.models import Airport

    if not DB_PATH.exists() or not inspect(engine).has_table("airport"):
        return False
    with Session(engine) as session:
        return session.exec(select(Airport).limit(1)).first() is not None
