from sqlalchemy import JSON, Column, DateTime, Integer, String

from app.core.database import Base
from app.core.time import utcnow


class Acceso(Base):
    __tablename__ = "accesos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_email = Column(String(200), unique=True, nullable=False, index=True)
    paginas = Column(JSON, nullable=False, default=list)
    actualizado = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)
