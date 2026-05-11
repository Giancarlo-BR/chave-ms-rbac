from pydantic import BaseModel, Field


class CurrentUser(BaseModel):
    """Representa o usuário extraído do payload do JWT."""

    sub: str
    email: str | None = None
    roles: list[str] = Field(default_factory=list)


class PublicMessage(BaseModel):
    message: str


class UserResponse(BaseModel):
    sub: str
    email: str | None = None
    roles: list[str]
