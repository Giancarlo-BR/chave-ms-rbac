from dataclasses import dataclass, field

import pytest
from fastapi.testclient import TestClient


@dataclass
class _Assignment:
    role: str
    assigned_by: int | None
    revoked: bool = False


@dataclass
class FakeRoleRepository:
    """Repositório em memória — espelha o contrato de RoleRepository."""

    catalog: set[str] = field(default_factory=lambda: {"admin", "user"})
    users: set[int] = field(default_factory=set)
    assignments: dict[int, list[_Assignment]] = field(default_factory=dict)

    def register_user(self, user_id: int) -> bool:
        if user_id in self.users:
            return False
        self.users.add(user_id)
        self.assignments.setdefault(user_id, [])
        return True

    def user_exists(self, user_id: int) -> bool:
        return user_id in self.users

    def fetch_roles(self, user_id: int) -> list[str]:
        return sorted(
            a.role for a in self.assignments.get(user_id, []) if not a.revoked
        )

    def role_in_catalog(self, role: str) -> bool:
        return role in self.catalog

    def assign_role(
        self, user_id: int, role: str, assigned_by: int | None
    ) -> bool:
        active = [
            a for a in self.assignments[user_id] if a.role == role and not a.revoked
        ]
        if active:
            return False
        self.assignments[user_id].append(_Assignment(role, assigned_by))
        return True

    def revoke_role(self, user_id: int, role: str) -> bool:
        revoked_any = False
        for a in self.assignments.get(user_id, []):
            if a.role == role and not a.revoked:
                a.revoked = True
                revoked_any = True
        return revoked_any


@pytest.fixture
def fake_repo() -> FakeRoleRepository:
    return FakeRoleRepository()


@pytest.fixture
def client(fake_repo: FakeRoleRepository) -> TestClient:
    from src.db import get_repo
    from src.main import app

    app.dependency_overrides[get_repo] = lambda: fake_repo
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
