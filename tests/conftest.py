import os
import tempfile
from pathlib import Path

# La configuration de test doit être définie avant l'import de l'application
_TMP_DIR = Path(tempfile.mkdtemp(prefix="barry-cms-tests-"))
os.environ["DATABASE_URL"] = f"sqlite:///{(_TMP_DIR / 'test.db').as_posix()}"
os.environ["MEDIA_DIR"] = str(_TMP_DIR / "media")
os.environ["SECRET_KEY"] = "test-secret-key-long-enough-for-hs256-signatures"
os.environ["ADMIN_USERNAME"] = "admin"
os.environ["ADMIN_PASSWORD"] = "test-password"
os.environ["ENVIRONMENT"] = "test"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from db.base import Base  # noqa: E402
from db.session import engine  # noqa: E402
from main import app  # noqa: E402

ADMIN_CREDENTIALS = {"username": "admin", "password": "test-password"}


@pytest.fixture
def client():
    # Base vierge à chaque test : le lifespan recrée les tables et le contenu initial
    Base.metadata.drop_all(engine)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers(client) -> dict[str, str]:
    response = client.post("/api/auth/login", data=ADMIN_CREDENTIALS)
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
