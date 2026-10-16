from sqlalchemy import JSON, Column, DateTime, ForeignKey, Index, Integer, String

from app.core.database import Base
from app.core.time import utcnow


class ContenidoSeccion(Base):
    __tablename__ = "contenido_secciones"

    proyecto_id = Column(Integer, ForeignKey("proyectos.id", ondelete="CASCADE"), primary_key=True)
    id = Column(String(120), primary_key=True)
    orden = Column(Integer, nullable=False, default=0)
    datos = Column(JSON, nullable=False)
    actualizado = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    autor_email = Column(String(200), nullable=False, default="")


class ContenidoProcedimiento(Base):
    __tablename__ = "contenido_procedimientos"

    proyecto_id = Column(Integer, ForeignKey("proyectos.id", ondelete="CASCADE"), primary_key=True)
    id = Column(String(120), primary_key=True)
    orden = Column(Integer, nullable=False, default=0)
    datos = Column(JSON, nullable=False)
    actualizado = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    autor_email = Column(String(200), nullable=False, default="")


class ContenidoVersion(Base):
    __tablename__ = "contenido_versiones"
    __table_args__ = (Index("ix_contenido_versiones_objeto", "proyecto_id", "tipo", "objeto_id"),)

    id = Column(Integer, primary_key=True)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id", ondelete="CASCADE"), nullable=False)
    tipo = Column(String(20), nullable=False)
    objeto_id = Column(String(120), nullable=False)
    accion = Column(String(20), nullable=False)
    datos = Column(JSON, nullable=True)
    autor_email = Column(String(200), nullable=False, default="")
    creado = Column(DateTime(timezone=True), nullable=False, default=utcnow)


class ContenidoMedia(Base):
    __tablename__ = "contenido_media"

    proyecto_id = Column(Integer, ForeignKey("proyectos.id", ondelete="CASCADE"), primary_key=True)
    procedimiento_id = Column(String(120), primary_key=True)
    archivo = Column(String(200), nullable=False)
    mime = Column(String(60), nullable=False)
    tamano = Column(Integer, nullable=False)
    huella = Column(String(64), nullable=False)
    subido = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    autor_email = Column(String(200), nullable=False, default="")
