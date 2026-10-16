from sqlalchemy import JSON, Boolean, Column, ForeignKey, Integer, String, Text

from app.core.database import Base


class Rol(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    clave = Column(String(60), unique=True, nullable=False, index=True)
    nombre = Column(String(120), nullable=False)
    descripcion = Column(Text, nullable=False, default="")
    permisos = Column(JSON, nullable=False, default=list)
    sistema = Column(Boolean, nullable=False, default=False)


class UsuarioRol(Base):
    __tablename__ = "usuario_roles"

    usuario_id = Column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    rol_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
