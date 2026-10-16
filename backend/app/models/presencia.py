from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.core.database import Base
from app.core.time import utcnow


class Presencia(Base):
    __tablename__ = "presencias"

    usuario_email = Column(String(200), primary_key=True)
    nombre = Column(String(200), nullable=False, default="")
    ruta = Column(String(300), nullable=False, default="")
    caso_id = Column(String(60), nullable=True)
    paso = Column(Integer, nullable=True)
    seccion_id = Column(String(120), nullable=True)
    accion = Column(String(30), nullable=False, default="viendo")
    ronda_id = Column(Integer, nullable=True)
    proyecto_id = Column(
        Integer, ForeignKey("proyectos.id", ondelete="SET NULL"), nullable=True, index=True
    )
    actualizado = Column(DateTime(timezone=True), nullable=False, default=utcnow, index=True)
