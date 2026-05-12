from typing import Iterator

from fastapi import Depends
from psycopg import Connection
from psycopg_pool import ConnectionPool

from .config import Settings, get_settings

_pool: ConnectionPool | None = None


def get_pool(settings: Settings | None = None) -> ConnectionPool:
    """Pool de conexões Postgres, inicializado preguiçosamente.

    Trade-off (ADR): pool global vs. pool injetado. Para o T1 acadêmico
    o singleton é suficiente; em produção colocaríamos o pool no
    `app.state` via lifespan.
    """
    global _pool
    if _pool is None:
        cfg = settings or get_settings()
        conninfo = (
            f"host={cfg.db_host} port={cfg.db_port} dbname={cfg.db_name} "
            f"user={cfg.db_user} password={cfg.db_password}"
        )
        _pool = ConnectionPool(conninfo, min_size=1, max_size=4, open=True)
    return _pool


def get_db_conn() -> Iterator[Connection]:
    """Dependency FastAPI: cede uma conexão do pool e a devolve no fim."""
    with get_pool().connection() as conn:
        yield conn


def get_repo(
    conn: Connection = Depends(get_db_conn),
):
    """Dependency FastAPI: instancia o repositório com a conexão atual."""
    # Importação local para evitar ciclo (repositories importa schemas).
    from .repositories import PostgresRoleRepository

    return PostgresRoleRepository(conn)
