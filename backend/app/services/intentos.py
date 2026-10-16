from datetime import timedelta

from fastapi import HTTPException, Request, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.core.time import utcnow
from app.models.cuenta import IntentoEntrada

VENTANA = timedelta(minutes=15)
MAXIMO = 5


def ip_de(request: Request) -> str:
    return request.headers.get("x-real-ip") or (request.client.host if request.client else "")


def claves(email: str, ip: str) -> list[str]:
    return [f"correo:{email}", f"ip:{ip}"]


def exigir_margen(db: Session, llaves: list[str]) -> None:
    db.execute(delete(IntentoEntrada).where(IntentoEntrada.momento < utcnow() - VENTANA))
    db.commit()
    for llave in llaves:
        fallidos = db.scalar(
            select(func.count(IntentoEntrada.id)).where(IntentoEntrada.clave == llave)
        )
        if fallidos >= MAXIMO:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Demasiados intentos; espera unos minutos antes de volver a intentar",
                headers={"Retry-After": str(int(VENTANA.total_seconds()))},
            )


def registrar_fallo(db: Session, llaves: list[str]) -> None:
    db.add_all(IntentoEntrada(clave=llave) for llave in llaves)
    db.commit()


def olvidar(db: Session, llave: str) -> None:
    db.execute(delete(IntentoEntrada).where(IntentoEntrada.clave == llave))
    db.commit()
