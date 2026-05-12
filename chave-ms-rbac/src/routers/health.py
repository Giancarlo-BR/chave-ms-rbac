from fastapi import APIRouter

from ..schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Health check")
def health() -> HealthResponse:
    """Endpoint usado pelo Docker Compose para verificar o serviço."""
    return HealthResponse(status="ok")
