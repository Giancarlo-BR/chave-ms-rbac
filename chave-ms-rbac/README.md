# chave-ms-rbac

Microsserviço de **Autorização (RBAC)** do projeto **Chave**.

Mantém o mapeamento `UserID → Roles` em banco Postgres dedicado
(`AuthorizationDB`) e expõe operações REST consumidas pelo serviço de
**Autenticação** (chave-mahakali-authenticator): `Register-User`, `Get-Roles`,
atribuir e revogar roles.

> Não decodifica JWT, não autentica nada. A emissão dos tokens é
> responsabilidade do Authenticator, que durante o login e o refresh chama
> este serviço para popular o claim `roles` do JWT.

---

## Tecnologias

- Python 3.12 + FastAPI
- PostgreSQL via `psycopg` 3 + `psycopg-pool`
- `pydantic-settings` para configuração via env
- `pytest` para testes unitários (fake repository in-memory)

---

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| GET | `/health` | Health check para o Docker Compose |
| POST | `/internal/users` | `Register-User`: cria registro mestre para um `user_id`. Idempotente |
| GET | `/internal/users/{user_id}/roles` | `Get-Roles`: retorna as roles ativas do usuário |
| POST | `/internal/users/{user_id}/roles` | Atribui uma role do catálogo |
| DELETE | `/internal/users/{user_id}/roles/{role}` | Revoga (soft-delete) uma role |

Swagger automático em `http://localhost:8000/docs`.

---

## Modelo de dados

Tabelas em `sql/init.sql`, carregadas pelo Postgres no primeiro start:

- `roles(role_id PK, name UNIQUE, description)` — catálogo. Roles são
  strings opacas; novas roles entram por dados, não por código.
- `user_roles(user_id PK, created_at)` — registro mestre por usuário.
- `user_role_assignments(id PK, user_id FK, role_id FK, assigned_at,
  assigned_by, revoked_at)` — N:N com histórico. Revogação é soft
  (`revoked_at`), nunca delete.

Seed inicial: `admin`, `user`.

---

## Variáveis de ambiente

```bash
cp .env.example .env
```

| Variável | Padrão | Descrição |
|---|---|---|
| `DB_HOST` | `localhost` | Host do Postgres |
| `DB_PORT` | `5432` | Porta do Postgres |
| `DB_NAME` | `chave_rbac` | Banco dedicado |
| `DB_USER` | `rbac` | Usuário do banco |
| `DB_PASSWORD` | `rbac_secret` | Senha do banco |
| `PORT` | `8000` | Porta do servidor |

---

## Desenvolvimento local

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
pytest -q                       # roda os testes (fake repo, sem Postgres)
```

Para subir o servidor localmente, é necessário um Postgres acessível
nas variáveis acima. A forma recomendada é via stack completa:

```bash
cd ../chave-infra && make setup
```

O serviço fica em `http://localhost:${MS_RBAC_PORT:-3002}` e o banco
dedicado em `chave-ms-rbac-db:5432` dentro da rede do Compose.

---

## Decisões arquiteturais (insumo para o ADR)

- **Banco dedicado** (`AuthorizationDB` ≠ `AuthenticationDB`): mantém
  bounded contexts independentes; mudanças no schema da Autenticação não
  quebram o RBAC.
- **Soft-delete em atribuições**: preserva histórico/auditoria.
- **`AuthorizationAudit` fora do MVP**: documentado como dívida; adicionar
  uma tabela `authorization_audit` não muda a API pública.
- **REST em vez de gRPC**: alinhado com o swagger da Authentication
  (Mahakali); reaproveita Swagger gratuito do FastAPI.
- **`psycopg` síncrono + pool**: ergonomia maior que `asyncpg` para a
  carga acadêmica; pool evita reabrir conexão por request.
