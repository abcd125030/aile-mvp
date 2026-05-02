from types import SimpleNamespace
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.dependencies.auth import get_current_user
from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def fake_user():
    return SimpleNamespace(
        id="a0000000-0000-0000-0000-000000000001",
        phone="13800000001",
        nickname="艾学同学",
        grade="高二",
        textbook_version="人教版A版",
        settings={},
        current_plan_id="b0000000-0000-0000-0000-000000000001",
        current_plan=None,
    )


@pytest.fixture
def authorized_user(fake_user):
    app.dependency_overrides[get_current_user] = lambda: fake_user
    yield fake_user
    app.dependency_overrides.pop(get_current_user, None)
