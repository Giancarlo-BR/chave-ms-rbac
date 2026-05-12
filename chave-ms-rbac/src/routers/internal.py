from fastapi import APIRouter, Depends, HTTPException, Response, status

from ..db import get_repo
from ..repositories import RoleRepository
from ..schemas import (
    AssignRoleRequest,
    AssignRoleResponse,
    RegisterUserRequest,
    RegisterUserResponse,
    RolesResponse,
)

router = APIRouter(prefix="/internal", tags=["internal"])


@router.post(
    "/users",
    response_model=RegisterUserResponse,
    summary="Register-User: cria registro mestre de roles para um UserID",
)
def register_user(
    body: RegisterUserRequest,
    response: Response,
    repo: RoleRepository = Depends(get_repo),
) -> RegisterUserResponse:
    """Chamado pelo Gateway após `Create-Account` da Authentication.

    Idempotente: nova chamada para o mesmo `user_id` devolve 200 em vez
    de 201, sem recriar nada.
    """
    created = repo.register_user(body.user_id)
    response.status_code = (
        status.HTTP_201_CREATED if created else status.HTTP_200_OK
    )
    return RegisterUserResponse(user_id=body.user_id, created=created)


@router.get(
    "/users/{user_id}/roles",
    response_model=RolesResponse,
    summary="Get-Roles: retorna as roles ativas do UserID",
)
def get_roles(
    user_id: int,
    repo: RoleRepository = Depends(get_repo),
) -> RolesResponse:
    """Chamado pelo Gateway a cada login/refresh para montar o claim
    `roles` do JWT. 404 se o usuário nunca foi registrado.
    """
    if not repo.user_exists(user_id):
        raise HTTPException(status_code=404, detail="Usuário não registrado")
    return RolesResponse(user_id=user_id, roles=repo.fetch_roles(user_id))


@router.post(
    "/users/{user_id}/roles",
    response_model=AssignRoleResponse,
    summary="Atribui uma role do catálogo ao usuário",
)
def assign_role(
    user_id: int,
    body: AssignRoleRequest,
    response: Response,
    repo: RoleRepository = Depends(get_repo),
) -> AssignRoleResponse:
    """Idempotente: se a role já estiver atribuída e ativa, devolve 200
    em vez de 201. Retorna 404 se o usuário não foi registrado e 400 se
    a role não existir no catálogo.
    """
    if not repo.user_exists(user_id):
        raise HTTPException(status_code=404, detail="Usuário não registrado")
    if not repo.role_in_catalog(body.role):
        raise HTTPException(status_code=400, detail="Role inexistente no catálogo")

    assigned = repo.assign_role(user_id, body.role, body.assigned_by)
    response.status_code = (
        status.HTTP_201_CREATED if assigned else status.HTTP_200_OK
    )
    return AssignRoleResponse(user_id=user_id, role=body.role, assigned=assigned)


@router.delete(
    "/users/{user_id}/roles/{role}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoga (soft-delete) uma role do usuário",
)
def revoke_role(
    user_id: int,
    role: str,
    repo: RoleRepository = Depends(get_repo),
) -> Response:
    """Marca `revoked_at` na atribuição ativa, preservando o histórico.
    Idempotente: 204 também se a role já não estava ativa.
    """
    if not repo.user_exists(user_id):
        raise HTTPException(status_code=404, detail="Usuário não registrado")
    repo.revoke_role(user_id, role)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
