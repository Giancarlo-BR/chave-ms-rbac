# chave-ms-rbac

Microsserviço de **Autorização (RBAC)** do projeto **Chave**.

Decodifica e valida JWTs emitidos pelo `chave-ms-auth` (HS256, `JWT_SECRET` compartilhado) e aplica controle de acesso a partir do claim `roles` do payload. Sem signup, sem geração de tokens — escopo restrito à autorização.

---

## Tecnologias

- Python 3.12 + FastAPI
- `python-jose` — decodificação JWT (HS256)
- `pydantic-settings` — configuração via variáveis de ambiente
- `pytest` — testes unitários

---

## Endpoints

| Método | Rota | Restrição |
|---|---|---|
| GET | `/public` | nenhuma |
| GET | `/protected/user` | JWT válido (qualquer role) |
| GET | `/protected/admin` | JWT válido + role `admin` |

Swagger automático em `http://localhost:8000/docs`.

---

## Variáveis de ambiente

```bash
cp .env.example .env
```

| Variável | Padrão | Descrição |
|---|---|---|
| `JWT_SECRET` | `change-me` | Segredo HS256 compartilhado com o chave-ms-auth |
| `JWT_ALGORITHM` | `HS256` | Algoritmo de assinatura |
| `PORT` | `8000` | Porta do servidor |

---

## Desenvolvimento local

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
pytest -q                       # 6 testes verdes
uvicorn src.main:app --reload   # sobe o servidor em :8000
```

---

## Stack completa

Executado pelo `chave-infra` via Docker Compose:

```bash
cd ../chave-infra && make setup
```

O serviço fica em `http://localhost:${MS_RBAC_PORT:-3002}`.
