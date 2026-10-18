from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String

from app.core.database import Base
from app.core.time import utcnow

VISTAS = ("general", "grafo")
SEGUNDOS_POR_OMISION = 20


class Pantalla(Base):
    __tablename__ = "pantallas"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(120), nullable=False)
    token_hash = Column(String(64), unique=True, nullable=False, index=True)
    vistas = Column(JSON, nullable=False, default=lambda: list(VISTAS))
    segundos = Column(Integer, nullable=False, default=SEGUNDOS_POR_OMISION)
    proyectos = Column(JSON, nullable=False, default=list)
    activa = Column(Boolean, nullable=False, default=True)
    creada = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    ultimo_uso = Column(DateTime(timezone=True), nullable=True)
    autor_email = Column(String(200), nullable=False, default="")
