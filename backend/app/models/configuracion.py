from sqlalchemy import JSON, Column, DateTime, String

from app.core.database import Base
from app.core.time import utcnow


class Configuracion(Base):
    __tablename__ = "configuracion"

    clave = Column(String(40), primary_key=True)
    valor = Column(JSON, nullable=False)
    actualizado = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    autor_email = Column(String(200), nullable=False, default="")
