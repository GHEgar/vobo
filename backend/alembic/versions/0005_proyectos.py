"""proyectos

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-16 07:37:01.304188
"""

from collections.abc import Sequence
from pathlib import Path

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: str | Sequence[str] | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

CLAVE = "principal"
NOMBRE = "Principal"
DOCUMENTOS = ("contenido_secciones", "contenido_procedimientos")
OPCIONALES = ("avisos", "presencias")


def _fk(tabla: str) -> str:
    return f"fk_{tabla}_proyecto_id"


def _nombre_de_archivos() -> str:
    try:
        from app.core.config import settings
        from app.services import instancia

        return instancia.leer(Path(settings.contenido_dir), []).nombre.strip()
    except Exception:
        return ""


def _nombre(conexion: sa.Connection) -> str:
    configuracion = sa.table("configuracion", sa.column("clave"), sa.column("valor", sa.JSON))
    valor = conexion.scalar(
        sa.select(configuracion.c.valor).where(configuracion.c.clave == "nombre")
    )
    if isinstance(valor, str) and valor.strip():
        return valor.strip()[:120]
    return (_nombre_de_archivos() or NOMBRE)[:120]


def _proyecto_fk(ondelete: str | None = "CASCADE") -> sa.ForeignKey:
    return sa.ForeignKey("proyectos.id", ondelete=ondelete)


def _documento(tabla: str) -> sa.Table:
    return sa.Table(
        tabla,
        sa.MetaData(),
        sa.Column("id", sa.String(length=120), nullable=False),
        sa.Column("orden", sa.Integer(), nullable=False),
        sa.Column("datos", sa.JSON(), nullable=False),
        sa.Column("actualizado", sa.DateTime(timezone=True), nullable=False),
        sa.Column("autor_email", sa.String(length=200), nullable=False),
        sa.Column("proyecto_id", sa.Integer(), _proyecto_fk(), nullable=False),
        sa.PrimaryKeyConstraint("proyecto_id", "id"),
    )


def _media() -> sa.Table:
    return sa.Table(
        "contenido_media",
        sa.MetaData(),
        sa.Column("procedimiento_id", sa.String(length=120), nullable=False),
        sa.Column("archivo", sa.String(length=200), nullable=False),
        sa.Column("mime", sa.String(length=60), nullable=False),
        sa.Column("tamano", sa.Integer(), nullable=False),
        sa.Column("huella", sa.String(length=64), nullable=False),
        sa.Column("subido", sa.DateTime(timezone=True), nullable=False),
        sa.Column("autor_email", sa.String(length=200), nullable=False),
        sa.Column("proyecto_id", sa.Integer(), _proyecto_fk(), nullable=False),
        sa.PrimaryKeyConstraint("proyecto_id", "procedimiento_id"),
    )


def _con_proyecto(tabla: str, proyecto_id: int) -> None:
    op.add_column(tabla, sa.Column("proyecto_id", sa.Integer(), nullable=True))
    op.execute(sa.text(f'UPDATE "{tabla}" SET proyecto_id = :p').bindparams(p=proyecto_id))


def upgrade() -> None:
    op.create_table(
        "proyectos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("clave", sa.String(length=60), nullable=False),
        sa.Column("nombre", sa.String(length=120), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=False),
        sa.Column("color_nombre", sa.String(length=7), nullable=True),
        sa.Column("orden", sa.Integer(), nullable=False),
        sa.Column("archivado", sa.Boolean(), nullable=False),
        sa.Column("por_omision", sa.Boolean(), nullable=False),
        sa.Column("creado", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("proyectos", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_proyectos_clave"), ["clave"], unique=True)

    conexion = op.get_bind()
    proyectos = sa.table(
        "proyectos",
        sa.column("id", sa.Integer),
        sa.column("clave", sa.String),
        sa.column("nombre", sa.String),
        sa.column("descripcion", sa.Text),
        sa.column("orden", sa.Integer),
        sa.column("archivado", sa.Boolean),
        sa.column("por_omision", sa.Boolean),
        sa.column("creado", sa.DateTime(timezone=True)),
    )
    conexion.execute(
        proyectos.insert().values(
            clave=CLAVE,
            nombre=_nombre(conexion),
            descripcion="",
            orden=0,
            archivado=False,
            por_omision=True,
            creado=sa.func.current_timestamp(),
        )
    )
    proyecto_id = conexion.scalar(sa.select(proyectos.c.id).where(proyectos.c.clave == CLAVE))

    _con_proyecto("rondas", proyecto_id)
    with op.batch_alter_table("rondas", schema=None) as batch_op:
        batch_op.alter_column("proyecto_id", existing_type=sa.Integer(), nullable=False)
        batch_op.create_index(batch_op.f("ix_rondas_proyecto_id"), ["proyecto_id"], unique=False)
        batch_op.create_foreign_key(_fk("rondas"), "proyectos", ["proyecto_id"], ["id"])

    for tabla in DOCUMENTOS:
        _con_proyecto(tabla, proyecto_id)
        with op.batch_alter_table(tabla, recreate="always", copy_from=_documento(tabla)):
            pass
    _con_proyecto("contenido_media", proyecto_id)
    with op.batch_alter_table("contenido_media", recreate="always", copy_from=_media()):
        pass

    _con_proyecto("contenido_versiones", proyecto_id)
    with op.batch_alter_table("contenido_versiones", schema=None) as batch_op:
        batch_op.alter_column("proyecto_id", existing_type=sa.Integer(), nullable=False)
        batch_op.drop_index("ix_contenido_versiones_objeto")
        batch_op.create_index(
            "ix_contenido_versiones_objeto", ["proyecto_id", "tipo", "objeto_id"], unique=False
        )
        batch_op.create_foreign_key(
            _fk("contenido_versiones"), "proyectos", ["proyecto_id"], ["id"], ondelete="CASCADE"
        )

    for tabla in OPCIONALES:
        _con_proyecto(tabla, proyecto_id)
        with op.batch_alter_table(tabla, schema=None) as batch_op:
            batch_op.create_index(batch_op.f(f"ix_{tabla}_proyecto_id"), ["proyecto_id"])
            batch_op.create_foreign_key(
                _fk(tabla), "proyectos", ["proyecto_id"], ["id"], ondelete="SET NULL"
            )


def _documento_viejo(tabla: str) -> sa.Table:
    return sa.Table(
        tabla,
        sa.MetaData(),
        sa.Column("id", sa.String(length=120), nullable=False),
        sa.Column("orden", sa.Integer(), nullable=False),
        sa.Column("datos", sa.JSON(), nullable=False),
        sa.Column("actualizado", sa.DateTime(timezone=True), nullable=False),
        sa.Column("autor_email", sa.String(length=200), nullable=False),
        sa.Column("proyecto_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def _media_vieja() -> sa.Table:
    return sa.Table(
        "contenido_media",
        sa.MetaData(),
        sa.Column("procedimiento_id", sa.String(length=120), nullable=False),
        sa.Column("archivo", sa.String(length=200), nullable=False),
        sa.Column("mime", sa.String(length=60), nullable=False),
        sa.Column("tamano", sa.Integer(), nullable=False),
        sa.Column("huella", sa.String(length=64), nullable=False),
        sa.Column("subido", sa.DateTime(timezone=True), nullable=False),
        sa.Column("autor_email", sa.String(length=200), nullable=False),
        sa.Column("proyecto_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("procedimiento_id"),
    )


def downgrade() -> None:
    conexion = op.get_bind()
    omision = conexion.scalar(sa.text("SELECT id FROM proyectos WHERE por_omision = 1 LIMIT 1"))
    for tabla in (*DOCUMENTOS, "contenido_media", "contenido_versiones"):
        op.execute(sa.text(f'DELETE FROM "{tabla}" WHERE proyecto_id != :p').bindparams(p=omision))

    for tabla in OPCIONALES:
        with op.batch_alter_table(tabla, schema=None) as batch_op:
            batch_op.drop_constraint(_fk(tabla), type_="foreignkey")
            batch_op.drop_index(batch_op.f(f"ix_{tabla}_proyecto_id"))
            batch_op.drop_column("proyecto_id")

    with op.batch_alter_table("contenido_versiones", schema=None) as batch_op:
        batch_op.drop_constraint(_fk("contenido_versiones"), type_="foreignkey")
        batch_op.drop_index("ix_contenido_versiones_objeto")
        batch_op.create_index("ix_contenido_versiones_objeto", ["tipo", "objeto_id"], unique=False)
        batch_op.drop_column("proyecto_id")

    with op.batch_alter_table("contenido_media", recreate="always", copy_from=_media_vieja()) as b:
        b.drop_column("proyecto_id")
    for tabla in DOCUMENTOS:
        with op.batch_alter_table(
            tabla, recreate="always", copy_from=_documento_viejo(tabla)
        ) as batch_op:
            batch_op.drop_column("proyecto_id")

    with op.batch_alter_table("rondas", schema=None) as batch_op:
        batch_op.drop_constraint(_fk("rondas"), type_="foreignkey")
        batch_op.drop_index(batch_op.f("ix_rondas_proyecto_id"))
        batch_op.drop_column("proyecto_id")

    with op.batch_alter_table("proyectos", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_proyectos_clave"))

    op.drop_table("proyectos")
