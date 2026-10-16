from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from app.core.database import Base
from app.core.time import utcnow

CLAVE_POR_OMISION = "principal"
NOMBRE_POR_OMISION = "Principal"


class Proyecto(Base):
    __tablename__ = "proyectos"

    id = Column(Integer, primary_key=True)
    clave = Column(String(60), unique=True, nullable=False, index=True)
    nombre = Column(String(120), nullable=False)
    descripcion = Column(Text, nullable=False, default="")
    color_nombre = Column(String(7), nullable=True)
    orden = Column(Integer, nullable=False, default=0)
    archivado = Column(Boolean, nullable=False, default=False)
    por_omision = Column(Boolean, nullable=False, default=False)
    creado = Column(DateTime(timezone=True), nullable=False, default=utcnow)
