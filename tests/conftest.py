import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ.pop("OPENAI_API_KEY", None)

from fastapi.testclient import TestClient  # noqa: E402

from app.database.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402

SAMPLE_CSV = ROOT / "sample_prospects.csv"


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def imported(client):
    with open(SAMPLE_CSV, "rb") as f:
        r = client.post("/api/companies/upload-csv", files={"file": ("p.csv", f, "text/csv")})
    assert r.status_code == 200, r.text
    return client.get("/api/prospects/").json()


class FakeOpenAI:
    """Records calls and returns a canned completion."""

    def __init__(self, content="SUBJECT: Hello John\nBODY:\nHi John,\nGreat to meet you."):
        self.calls = []
        self.content = content
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=self.content))])


@pytest.fixture
def fake_openai(monkeypatch):
    fake = FakeOpenAI()
    from app.services import email_service

    monkeypatch.setattr(email_service, "get_openai_client", lambda: fake)
    return fake
