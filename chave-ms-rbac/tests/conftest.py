import time
from typing import Callable

import pytest
from fastapi.testclient import TestClient
from jose import jwt

TEST_SECRET = "test-secret"
TEST_ALGORITHM = "HS256"


@pytest.fixture(autouse=True)
def _set_test_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Garante segredo conhecido e cache limpo entre testes."""
    monkeypatch.setenv("JWT_SECRET", TEST_SECRET)
    monkeypatch.setenv("JWT_ALGORITHM", TEST_ALGORITHM)
    from src.config import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def client() -> TestClient:
    from src.main import app

    return TestClient(app)


@pytest.fixture
def make_token() -> Callable[..., str]:
    """Fabrica JWTs locais simulando o chave-ms-auth."""

    def _make(
        roles: list[str] | None = None,
        sub: str = "user-1",
        email: str = "user@example.com",
        expires_in_seconds: int = 900,
        secret: str = TEST_SECRET,
        algorithm: str = TEST_ALGORITHM,
    ) -> str:
        now = int(time.time())
        payload = {
            "sub": sub,
            "email": email,
            "roles": roles or [],
            "iat": now,
            "exp": now + expires_in_seconds,
        }
        return jwt.encode(payload, secret, algorithm=algorithm)

    return _make
