from typing import Callable

from fastapi.testclient import TestClient


def test_public_route_returns_200_without_token(client: TestClient) -> None:
    response = client.get("/public")
    assert response.status_code == 200
    assert response.json() == {"message": "Conteúdo público"}


def test_protected_user_without_token_returns_401(client: TestClient) -> None:
    response = client.get("/protected/user")
    assert response.status_code == 401
    assert response.json()["detail"] == "Token não fornecido"


def test_protected_user_with_expired_token_returns_401(
    client: TestClient, make_token: Callable[..., str]
) -> None:
    token = make_token(roles=["user"], expires_in_seconds=-10)
    response = client.get(
        "/protected/user",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Token expirado"


def test_protected_user_with_invalid_signature_returns_401(
    client: TestClient, make_token: Callable[..., str]
) -> None:
    token = make_token(roles=["user"], secret="outro-segredo")
    response = client.get(
        "/protected/user",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Token inválido"


def test_protected_admin_with_user_role_returns_403(
    client: TestClient, make_token: Callable[..., str]
) -> None:
    token = make_token(roles=["user"])
    response = client.get(
        "/protected/admin",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Permissão insuficiente"


def test_protected_admin_with_admin_role_returns_200(
    client: TestClient, make_token: Callable[..., str]
) -> None:
    token = make_token(roles=["admin"], sub="adm-1", email="admin@example.com")
    response = client.get(
        "/protected/admin",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["sub"] == "adm-1"
    assert body["roles"] == ["admin"]
