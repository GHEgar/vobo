from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)

from app.core.database import Base
from app.core.time import utcnow

ESTADOS_COMENTARIO = ("nuevo", "en_curso", "resuelto")
TIPOS_COMENTARIO = ("paso", "no_pude")
OBJETOS_SEGUIMIENTO = ("falla", "comentario")
ACCIONES_SEGUIMIENTO = ("respuesta", "estado", "plazo", "nota", "esfuerzo", "vinculo")
PASO_NO_PUDE = -1


class ComentarioSeguimiento(Base):
    __tablename__ = "comentarios_seguimiento"
    __table_args__ = (
        UniqueConstraint("ronda_id", "caso_id", "usuario_email", "paso", "tipo"),
        Index("ix_comentarios_seguimiento_principal", "principal_objeto", "principal_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    ronda_id = Column(
        Integer, ForeignKey("rondas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    caso_id = Column(String(60), nullable=False)
    usuario_email = Column(String(200), nullable=False)
    paso = Column(Integer, nullable=False)
    tipo = Column(
        Enum(*TIPOS_COMENTARIO, name="tipo_comentario", create_constraint=True), nullable=False
    )
    estado = Column(
        Enum(*ESTADOS_COMENTARIO, name="estado_comentario", create_constraint=True),
        nullable=False,
        default="nuevo",
    )
    plazo = Column(Date, nullable=True)
    plazo_por = Column(String(200), nullable=True)
    creado = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    resuelto_en = Column(DateTime(timezone=True), nullable=True)
    resuelto_por = Column(String(200), nullable=True)
    esfuerzo_horas = Column(Float, nullable=True)
    principal_objeto = Column(String(10), nullable=True)
    principal_id = Column(Integer, nullable=True)


class Seguimiento(Base):
    __tablename__ = "seguimiento"
    __table_args__ = (Index("ix_seguimiento_objeto", "objeto", "objeto_id"),)

    id = Column(Integer, primary_key=True, index=True)
    objeto = Column(
        Enum(*OBJETOS_SEGUIMIENTO, name="objeto_seguimiento", create_constraint=True),
        nullable=False,
    )
    objeto_id = Column(Integer, nullable=False)
    autor_email = Column(String(200), nullable=False)
    accion = Column(
        Enum(*ACCIONES_SEGUIMIENTO, name="accion_seguimiento", create_constraint=True),
        nullable=False,
    )
    texto = Column(Text, nullable=False, default="")
    anterior = Column(String(40), nullable=True)
    nuevo = Column(String(40), nullable=True)
    creado = Column(DateTime(timezone=True), nullable=False, default=utcnow, index=True)
