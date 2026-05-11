from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from pydantic import ValidationError

from .config import get_settings
from .schemas import CurrentUser

# tokenUrl aponta para o chave-ms-auth (rota POST /auth/login).
# auto_error=False — controlamos a mensagem de 401 manualmente.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
) -> CurrentUser:
    """Decodifica e valida o JWT do header Authorization.

    Trade-off (ADR): leitura stateless do claim `roles`. Em produção,
    RS256 + JWKS eliminaria o segredo compartilhado entre serviços.
    """
    if token is None:
        raise _unauthorized("Token não fornecido")

    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except ExpiredSignatureError:
        raise _unauthorized("Token expirado")
    except JWTError:
        raise _unauthorized("Token inválido")

    try:
        return CurrentUser(**payload)
    except ValidationError:
        raise _unauthorized("Payload do token inválido")


def RequireRole(*allowed: str) -> Callable[..., CurrentUser]:
    """Factory de dependência: exige ao menos uma das roles informadas.

    Trade-off (ADR): factory dá call-site idiomático
    (`Depends(RequireRole("admin"))`) e dispensa estado mutável.
    """
    allowed_set = set(allowed)

    def _dep(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not allowed_set.intersection(user.roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão insuficiente",
            )
        return user

    return _dep
