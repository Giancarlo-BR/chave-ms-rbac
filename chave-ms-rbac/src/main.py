from fastapi import FastAPI

from .routers import health, internal

app = FastAPI(
    title="chave-ms-rbac",
    version="0.1.0",
    description=(
        "Microsserviço de Autorização (RBAC) do projeto Chave. "
        "Mantém o mapeamento UserID → Roles em banco dedicado. "
        "Consumido pelo API Gateway via REST. Não decodifica JWT, "
        "não autentica — esse é papel do Gateway."
    ),
)

app.include_router(health.router)
app.include_router(internal.router)
