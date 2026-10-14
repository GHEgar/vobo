from pydantic import BaseModel


class SeccionResultadoResponse(BaseModel):
    afectados: int
    omitidos: int
    falla_id: int | None = None
