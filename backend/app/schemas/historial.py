from datetime import date

from pydantic import BaseModel


class PuntoAvance(BaseModel):
    fecha: date
    marcados_acumulados: int
    total: int
