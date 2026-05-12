from typing import Protocol

from psycopg import Connection


class RoleRepository(Protocol):
    """Contrato do repositório.

    Existe para permitir um fake in-memory nos testes via
    `app.dependency_overrides[get_repo]`.
    """

    def register_user(self, user_id: int) -> bool: ...
    def user_exists(self, user_id: int) -> bool: ...
    def fetch_roles(self, user_id: int) -> list[str]: ...
    def role_in_catalog(self, role: str) -> bool: ...
    def assign_role(
        self, user_id: int, role: str, assigned_by: int | None
    ) -> bool: ...
    def revoke_role(self, user_id: int, role: str) -> bool: ...


class PostgresRoleRepository:
    """Implementação Postgres síncrona via psycopg."""

    def __init__(self, conn: Connection) -> None:
        self.conn = conn

    def register_user(self, user_id: int) -> bool:
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO user_roles (user_id) VALUES (%s) "
                "ON CONFLICT (user_id) DO NOTHING",
                (user_id,),
            )
            created = cur.rowcount == 1
        self.conn.commit()
        return created

    def user_exists(self, user_id: int) -> bool:
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM user_roles WHERE user_id = %s",
                (user_id,),
            )
            return cur.fetchone() is not None

    def fetch_roles(self, user_id: int) -> list[str]:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT r.name
                FROM user_role_assignments ura
                JOIN roles r ON r.role_id = ura.role_id
                WHERE ura.user_id = %s AND ura.revoked_at IS NULL
                ORDER BY r.name
                """,
                (user_id,),
            )
            return [row[0] for row in cur.fetchall()]

    def role_in_catalog(self, role: str) -> bool:
        with self.conn.cursor() as cur:
            cur.execute("SELECT 1 FROM roles WHERE name = %s", (role,))
            return cur.fetchone() is not None

    def assign_role(
        self, user_id: int, role: str, assigned_by: int | None
    ) -> bool:
        # Idempotente: se já existe atribuição ativa, devolve False.
        # Pressupõe que role_in_catalog já foi validado pelo chamador.
        with self.conn.cursor() as cur:
            cur.execute("SELECT role_id FROM roles WHERE name = %s", (role,))
            row = cur.fetchone()
            assert row is not None, "role_in_catalog deve ser checado antes"
            role_id = row[0]

            cur.execute(
                """
                SELECT 1 FROM user_role_assignments
                WHERE user_id = %s AND role_id = %s AND revoked_at IS NULL
                """,
                (user_id, role_id),
            )
            if cur.fetchone() is not None:
                return False

            cur.execute(
                """
                INSERT INTO user_role_assignments
                    (user_id, role_id, assigned_by)
                VALUES (%s, %s, %s)
                """,
                (user_id, role_id, assigned_by),
            )
        self.conn.commit()
        return True

    def revoke_role(self, user_id: int, role: str) -> bool:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                UPDATE user_role_assignments
                SET revoked_at = NOW()
                WHERE id IN (
                    SELECT ura.id
                    FROM user_role_assignments ura
                    JOIN roles r ON r.role_id = ura.role_id
                    WHERE ura.user_id = %s
                      AND r.name = %s
                      AND ura.revoked_at IS NULL
                )
                """,
                (user_id, role),
            )
            revoked = cur.rowcount > 0
        self.conn.commit()
        return revoked
