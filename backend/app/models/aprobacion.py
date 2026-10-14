from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.time import utcnow

TIPOS_APROBACION = ("herramienta", "caracteristica")
ESTADOS_APROBACION = ("aprobada", "rechazada", "pendiente")


class Aprobacion(Base):
    __tablename__ = "aprobaciones"

    id = Column(Integer, primary_key=True, index=True)
    ronda_id = Column(
        Integer, ForeignKey("rondas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tipo = Column(
        Enum(*TIPOS_APROBACION, name="tipo_aprobacion", create_constraint=True), nullable=False
    )
    objetivo_id = Column(String(120), nullable=False, index=True)
    estado = Column(
        Enum(*ESTADOS_APROBACION, name="estado_aprobacion", create_constraint=True), nullable=False
    )
    comentario = Column(Text, nullable=False, default="")
    usuario_email = Column(String(200), nullable=False)
    usuario_nombre = Column(String(200), nullable=False, default="")
    creada = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    ronda = relationship("Ronda", back_populates="aprobaciones")
