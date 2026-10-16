from fastapi import APIRouter, Response

from app.core.config import settings
from app.schemas.instancia import VersionResponse

router = APIRouter(prefix="/api/version", tags=["version"])


@router.get("", response_model=VersionResponse)
def obtener_version(response: Response) -> VersionResponse:
    response.headers["Cache-Control"] = "no-store"
    return VersionResponse(version=settings.app_version)
