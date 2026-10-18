from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.time import utcnow

ESTADOS_RESULTADO = ("pendiente", "pasa", "falla", "no_pude")
ACCIONES_HISTORIAL = ("crear", "marcar", "cambiar", "limpiar", "paso")


class Resultado(Base):
    __tablename__ = "resultados"
    __table_args__ = (UniqueConstraint("ronda_id", "caso_id", "usuario_email"),)

    id = Column(Integer, primary_key=True, index=True)
    ronda_id = Column(
        Integer, ForeignKey("rondas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    caso_id = Column(String(60), nullable=False, index=True)
    usuario_email = Column(String(200), nullable=False, index=True)
    estado = Column(
        Enum(*ESTADOS_RESULTADO, name="estado_resultado", create_constraint=True),
        nullable=False,
        default="pendiente",
    )
    pasos_marcados = Column(JSON, nullable=False, default=list)
    comentario = Column(Text, nullable=True)
    actualizado = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    ronda = relationship("Ronda", back_populates="resultados")


class ResultadoHistorial(Base):
    __tablename__ = "resultados_historial"

    id = Column(Integer, primary_key=True, index=True)
    ronda_id = Column(
        Integer, ForeignKey("rondas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    caso_id = Column(String(60), nullable=False, index=True)
    usuario_email = Column(String(200), nullable=False, index=True)
    estado = Column(
        Enum(*ESTADOS_RESULTADO, name="estado_resultado", create_constraint=True),
        nullable=False,
    )
    paso = Column(Integer, nullable=True)
    accion = Column(
        Enum(*ACCIONES_HISTORIAL, name="accion_historial", create_constraint=True),
        nullable=False,
    )
    creado = Column(DateTime(timezone=True), nullable=False, default=utcnow, index=True)

    ronda = relationship("Ronda", back_populates="historial")
