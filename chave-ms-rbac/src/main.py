from fastapi import Depends, FastAPI

from .schemas import CurrentUser, PublicMessage, UserResponse
from .security import RequireRole, get_current_user

app = FastAPI(
    title="chave-ms-rbac",
    version="0.1.0",
    description=(
        "Microsserviço de Autorização (RBAC) do projeto Chave. "
        "Decodifica e valida JWTs emitidos pelo chave-ms-auth e aplica "
        "controle de acesso baseado em roles. Não realiza signup nem "
        "geração de tokens."
    ),
)


@app.get(
    "/public",
    response_model=PublicMessage,
    summary="Rota pública",
    tags=["public"],
)
def read_public() -> PublicMessage:
    """Rota aberta — não exige autenticação."""
    return PublicMessage(message="Conteúdo público")


@app.get(
    "/protected/user",
    response_model=UserResponse,
    summary="Rota protegida (qualquer usuário autenticado)",
    tags=["protected"],
)
def read_protected_user(
    user: CurrentUser = Depends(get_current_user),
) -> UserResponse:
    """Exige um JWT válido. Qualquer role do payload é aceita."""
    return UserResponse(sub=user.sub, email=user.email, roles=user.roles)


@app.get(
    "/protected/admin",
    response_model=UserResponse,
    summary="Rota protegida (apenas role 'admin')",
    tags=["protected"],
)
def read_protected_admin(
    user: CurrentUser = Depends(RequireRole("admin")),
) -> UserResponse:
    """Exige JWT válido contendo a role 'admin'. Caso contrário, 403."""
    return UserResponse(sub=user.sub, email=user.email, roles=user.roles)
