from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.time import utcnow

REPRODUCIBLE = ("siempre", "a_veces", "una_vez")
SEVERIDADES = ("critica", "alta", "media", "baja")
ESTADOS_FALLA = ("nueva", "en_curso", "lista_para_revalidar", "cerrada")
TIPOS_FALLA = ("falla", "no_pude")


class Falla(Base):
    __tablename__ = "fallas"

    id = Column(Integer, primary_key=True, index=True)
    ronda_id = Column(
        Integer, ForeignKey("rondas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    caso_id = Column(String(60), nullable=False, index=True)
    usuario_email = Column(String(200), nullable=False, index=True)
    paso = Column(Integer, nullable=True)
    seccion_id = Column(String(120), nullable=True, index=True)
    tipo = Column(String(10), nullable=False, default="falla", server_default="falla", index=True)
    obtenido = Column(Text, nullable=False)
    reproducible = Column(
        Enum(*REPRODUCIBLE, name="reproducible", create_constraint=True), nullable=False
    )
    severidad = Column(
        Enum(*SEVERIDADES, name="severidad", create_constraint=True), nullable=False, index=True
    )
    navegador = Column(String(400), nullable=False, default="")
    url = Column(String(500), nullable=False, default="")
    version_visible = Column(String(120), nullable=False, default="")
    creada = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    estado = Column(
        Enum(*ESTADOS_FALLA, name="estado_falla", create_constraint=True),
        nullable=False,
        default="nueva",
        index=True,
    )
    nota_resolucion = Column(Text, nullable=False, default="")
    plazo = Column(Date, nullable=True)
    plazo_por = Column(String(200), nullable=True)
    resuelta_en = Column(DateTime(timezone=True), nullable=True)
    resuelta_por = Column(String(200), nullable=True)

    ronda = relationship("Ronda", back_populates="fallas")
    evidencias = relationship("Evidencia", back_populates="falla", cascade="all, delete-orphan")


class Evidencia(Base):
    __tablename__ = "evidencias"

    id = Column(Integer, primary_key=True, index=True)
    falla_id = Column(
        Integer, ForeignKey("fallas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ruta = Column(String(300), nullable=False)
    mime = Column(String(40), nullable=False)
    creada = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    falla = relationship("Falla", back_populates="evidencias")
