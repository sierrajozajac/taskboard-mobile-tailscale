"""Test fixtures.

Env is set BEFORE importing the app so config.settings (and the SQLAlchemy engine,
built at import time) use a throwaway temp database and console printing.
"""

from __future__ import annotations

import os
import tempfile

# Must run before any `app.*` import.
_TMP_DB = os.path.join(tempfile.mkdtemp(prefix="taskboard-test-"), "test.db")
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP_DB}"
os.environ["PRINT_MODE"] = "console"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import SQLModel  # noqa: E402

from app.db import engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    # Fresh schema per test for isolation.
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def board(client):
    """A board created via the API (so it has default columns + a 'General' lane)."""
    resp = client.post("/boards", json={"name": "Test Board", "description": "x"})
    assert resp.status_code == 201, resp.text
    return resp.json()
