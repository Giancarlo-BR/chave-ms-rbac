from pydantic import BaseModel, Field


class RegisterUserRequest(BaseModel):
    user_id: int = Field(..., gt=0, description="UserID gerado pela Authentication")


class RegisterUserResponse(BaseModel):
    user_id: int
    created: bool = Field(
        ...,
        description="True se o registro foi criado agora, False se já existia",
    )


class AssignRoleRequest(BaseModel):
    role: str = Field(..., min_length=1, description="Nome da role no catálogo")
    assigned_by: int | None = Field(
        default=None,
        description="UserID do ator que está atribuindo (opcional)",
    )


class AssignRoleResponse(BaseModel):
    user_id: int
    role: str
    assigned: bool = Field(
        ...,
        description="True se atribuída agora, False se já estava ativa",
    )


class RolesResponse(BaseModel):
    user_id: int
    roles: list[str]


class HealthResponse(BaseModel):
    status: str = "ok"
