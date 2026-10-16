from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.time import utcnow


class Ronda(Base):
    __tablename__ = "rondas"

    id = Column(Integer, primary_key=True, index=True)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"), nullable=False, index=True)
    nombre = Column(String(120), nullable=False)
    snapshot = Column(String(200), nullable=False, default="")
    abierta = Column(Boolean, nullable=False, default=True)
    creada = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    asignaciones = relationship("Asignacion", back_populates="ronda", cascade="all, delete-orphan")
    resultados = relationship("Resultado", back_populates="ronda", cascade="all, delete-orphan")
    fallas = relationship("Falla", back_populates="ronda", cascade="all, delete-orphan")
    decisiones = relationship("Decision", back_populates="ronda", cascade="all, delete-orphan")
    aprobaciones = relationship("Aprobacion", back_populates="ronda", cascade="all, delete-orphan")


class Asignacion(Base):
    __tablename__ = "asignaciones"
    __table_args__ = (UniqueConstraint("ronda_id", "usuario_email", "seccion_id"),)

    id = Column(Integer, primary_key=True, index=True)
    ronda_id = Column(
        Integer, ForeignKey("rondas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    usuario_email = Column(String(200), nullable=False, index=True)
    seccion_id = Column(String(120), nullable=False)

    ronda = relationship("Ronda", back_populates="asignaciones")
