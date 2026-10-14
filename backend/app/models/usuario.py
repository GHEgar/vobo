from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.time import utcnow


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    sub_oidc = Column(String(64), unique=True, nullable=True, index=True)
    email = Column(String(200), unique=True, nullable=False, index=True)
    nombre = Column(String(200), nullable=False)
    ultimo_acceso = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    permisos = Column(JSON, nullable=True)

    sesiones = relationship("Sesion", back_populates="usuario", cascade="all, delete-orphan")


class Sesion(Base):
    __tablename__ = "sesiones"

    id = Column(String(64), primary_key=True)
    usuario_id = Column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    access_expira = Column(DateTime(timezone=True), nullable=False)
    permisos_locales = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    usuario = relationship("Usuario", back_populates="sesiones")
