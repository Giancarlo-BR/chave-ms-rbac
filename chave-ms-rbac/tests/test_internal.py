from fastapi.testclient import TestClient

from tests.conftest import FakeRoleRepository


def test_health_returns_200(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_register_user_creates_record_then_is_idempotent(
    client: TestClient, fake_repo: FakeRoleRepository
) -> None:
    first = client.post("/internal/users", json={"user_id": 42})
    assert first.status_code == 201
    assert first.json() == {"user_id": 42, "created": True}
    assert fake_repo.user_exists(42)

    second = client.post("/internal/users", json={"user_id": 42})
    assert second.status_code == 200
    assert second.json() == {"user_id": 42, "created": False}


def test_get_roles_returns_404_for_unregistered_user(client: TestClient) -> None:
    response = client.get("/internal/users/999/roles")
    assert response.status_code == 404
    assert response.json()["detail"] == "Usuário não registrado"


def test_assign_role_then_get_returns_it(
    client: TestClient, fake_repo: FakeRoleRepository
) -> None:
    fake_repo.register_user(42)
    response = client.post(
        "/internal/users/42/roles",
        json={"role": "admin", "assigned_by": 1},
    )
    assert response.status_code == 201
    assert response.json() == {"user_id": 42, "role": "admin", "assigned": True}

    roles = client.get("/internal/users/42/roles")
    assert roles.status_code == 200
    assert roles.json() == {"user_id": 42, "roles": ["admin"]}


def test_assign_role_is_idempotent(
    client: TestClient, fake_repo: FakeRoleRepository
) -> None:
    fake_repo.register_user(42)
    client.post("/internal/users/42/roles", json={"role": "admin"})
    second = client.post("/internal/users/42/roles", json={"role": "admin"})
    assert second.status_code == 200
    assert second.json() == {"user_id": 42, "role": "admin", "assigned": False}
    assert fake_repo.fetch_roles(42) == ["admin"]


def test_assign_role_rejects_unknown_role(
    client: TestClient, fake_repo: FakeRoleRepository
) -> None:
    fake_repo.register_user(42)
    response = client.post(
        "/internal/users/42/roles",
        json={"role": "dragon"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Role inexistente no catálogo"


def test_revoke_role_soft_deletes_and_removes_from_get(
    client: TestClient, fake_repo: FakeRoleRepository
) -> None:
    fake_repo.register_user(42)
    fake_repo.assign_role(42, "admin", assigned_by=None)
    response = client.delete("/internal/users/42/roles/admin")
    assert response.status_code == 204

    roles = client.get("/internal/users/42/roles")
    assert roles.json() == {"user_id": 42, "roles": []}
