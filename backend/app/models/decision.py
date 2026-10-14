from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.time import utcnow

DECISIONES = ("desplegar", "desplegar_con_aviso", "aplazar", "pendiente")


class Decision(Base):
    __tablename__ = "decisiones"
    __table_args__ = (UniqueConstraint("ronda_id", "herramienta_id"),)

    id = Column(Integer, primary_key=True, index=True)
    ronda_id = Column(
        Integer, ForeignKey("rondas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    herramienta_id = Column(String(120), nullable=False, index=True)
    decision = Column(
        Enum(*DECISIONES, name="decision", create_constraint=True),
        nullable=False,
        default="pendiente",
    )
    motivo = Column(Text, nullable=False, default="")
    decidido_por = Column(String(200), nullable=False, default="")
    actualizado = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    ronda = relationship("Ronda", back_populates="decisiones")
