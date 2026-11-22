"""Shared pytest fixtures.

The tests use a throwaway SQLite file (never your src/backend/data/cph.db), seeded with the
same deterministic synthetic data as `python src/backend/scripts/seed.py`.
"""

import os
import tempfile
from collections.abc import Iterator
from pathlib import Path

# Must be set before backend.app.db is imported anywhere.
os.environ["CPH_DB_PATH"] = str(Path(tempfile.mkdtemp(prefix="cph-test-")) / "test.db")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from backend.app.main import app  # noqa: E402
from backend.scripts.seed import seed_database  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def seeded_db() -> dict[str, int]:
    """Seed the test database once per test run and return the row counts."""
    return seed_database()


@pytest.fixture()
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client
