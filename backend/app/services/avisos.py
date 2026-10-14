from fastapi import HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.core.time import utcnow
from app.models.aviso import Aviso
from app.models.falla import Falla
from app.models.usuario import Usuario
from app.schemas.aviso import AvisoCreate

LIMITE = 100
TITULO_LIBRE = "Aviso de coordinación"


def listar(db: Session, email: str) -> list[Aviso]:
    consulta = (
        select(Aviso)
        .where(Aviso.usuario_email == email)
        .order_by(Aviso.creado.desc(), Aviso.id.desc())
        .limit(LIMITE)
    )
    return list(db.scalars(consulta))


def no_leidos(db: Session, email: str) -> int:
    consulta = select(func.count(Aviso.id)).where(
        Aviso.usuario_email == email, Aviso.leido.is_(None)
    )
    return db.scalar(consulta) or 0


def marcar(db: Session, email: str, aviso_id: int) -> Aviso:
    aviso = db.get(Aviso, aviso_id)
    if aviso is None or aviso.usuario_email != email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aviso no encontrado")
    if aviso.leido is None:
        aviso.leido = utcnow()
        db.commit()
        db.refresh(aviso)
    return aviso


def marcar_todos(db: Session, email: str) -> int:
    resultado = db.execute(
        update(Aviso)
        .where(Aviso.usuario_email == email, Aviso.leido.is_(None))
        .values(leido=utcnow())
    )
    db.commit()
    return resultado.rowcount or 0


def crear(db: Session, datos: AvisoCreate, autor_email: str, autor_nombre: str) -> list[Aviso]:
    destinatarios = list(datos.destinatarios)
    caso_id = None
    titulo = TITULO_LIBRE
    if datos.falla_id is not None:
        falla = db.get(Falla, datos.falla_id)
        if falla is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Falla no encontrada")
        caso_id = falla.caso_id
        titulo = f"Tu reporte de {caso_id} fue atendido"
        destinatarios = destinatarios or [falla.usuario_email]
    if datos.titulo and datos.titulo.strip():
        titulo = datos.titulo.strip()
    avisos = [
        Aviso(
            usuario_email=email,
            titulo=titulo,
            mensaje=datos.mensaje,
            falla_id=datos.falla_id,
            caso_id=caso_id,
            autor_email=autor_email,
            autor_nombre=autor_nombre,
        )
        for email in destinatarios
    ]
    db.add_all(avisos)
    db.commit()
    for aviso in avisos:
        db.refresh(aviso)
    return avisos


def personas(db: Session, excluir: str) -> list[Usuario]:
    consulta = select(Usuario).where(Usuario.email != excluir).order_by(Usuario.nombre)
    return list(db.scalars(consulta))
