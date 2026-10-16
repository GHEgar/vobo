from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.time import utcnow


class Aviso(Base):
    __tablename__ = "avisos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_email = Column(String(200), nullable=False, index=True)
    titulo = Column(String(200), nullable=False)
    mensaje = Column(Text, nullable=False)
    falla_id = Column(
        Integer, ForeignKey("fallas.id", ondelete="SET NULL"), nullable=True, index=True
    )
    caso_id = Column(String(60), nullable=True)
    proyecto_id = Column(
        Integer, ForeignKey("proyectos.id", ondelete="SET NULL"), nullable=True, index=True
    )
    autor_email = Column(String(200), nullable=False)
    autor_nombre = Column(String(200), nullable=False, default="")
    creado = Column(DateTime(timezone=True), nullable=False, default=utcnow, index=True)
    leido = Column(DateTime(timezone=True), nullable=True)

    proyecto = relationship("Proyecto", lazy="joined")

    @property
    def proyecto_clave(self) -> str | None:
        return self.proyecto.clave if self.proyecto is not None else None
