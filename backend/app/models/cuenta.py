from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String

from app.core.database import Base
from app.core.time import utcnow


class Cuenta(Base):
    __tablename__ = "cuentas"

    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True)
    hash = Column(String(200), nullable=False)
    activa = Column(Boolean, nullable=False, default=True)
    creada = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    ultimo_cambio = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    debe_cambiar = Column(Boolean, nullable=False, default=False)


class Invitacion(Base):
    __tablename__ = "invitaciones"

    id = Column(Integer, primary_key=True)
    token_hash = Column(String(64), unique=True, nullable=False)
    email = Column(String(200), nullable=False, index=True)
    roles = Column(JSON, nullable=False, default=list)
    creada_por = Column(String(200), nullable=False)
    creada = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    expira = Column(DateTime(timezone=True), nullable=False)
    usada = Column(DateTime(timezone=True), nullable=True)


class Restablecimiento(Base):
    __tablename__ = "restablecimientos"

    id = Column(Integer, primary_key=True)
    token_hash = Column(String(64), unique=True, nullable=False)
    usuario_id = Column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    creado_por = Column(String(200), nullable=False)
    creado = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    expira = Column(DateTime(timezone=True), nullable=False)
    usado = Column(DateTime(timezone=True), nullable=True)


class IntentoEntrada(Base):
    __tablename__ = "intentos_entrada"

    id = Column(Integer, primary_key=True)
    clave = Column(String(260), nullable=False, index=True)
    momento = Column(DateTime(timezone=True), nullable=False, default=utcnow, index=True)
