"""esquema base

Revision ID: 0001
Revises:
Create Date: 2026-10-15 22:22:59.466028
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLAS = (
    "accesos",
    "presencias",
    "rondas",
    "usuarios",
    "aprobaciones",
    "asignaciones",
    "decisiones",
    "fallas",
    "resultados",
    "sesiones",
    "avisos",
    "evidencias",
)


def upgrade() -> None:
    op.create_table(
        "accesos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_email", sa.String(length=200), nullable=False),
        sa.Column("paginas", sa.JSON(), nullable=False),
        sa.Column("actualizado", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_accesos_id", "accesos", ["id"], unique=False)
    op.create_index("ix_accesos_usuario_email", "accesos", ["usuario_email"], unique=True)

    op.create_table(
        "presencias",
        sa.Column("usuario_email", sa.String(length=200), nullable=False),
        sa.Column("nombre", sa.String(length=200), nullable=False),
        sa.Column("ruta", sa.String(length=300), nullable=False),
        sa.Column("caso_id", sa.String(length=60), nullable=True),
        sa.Column("paso", sa.Integer(), nullable=True),
        sa.Column("seccion_id", sa.String(length=120), nullable=True),
        sa.Column("accion", sa.String(length=30), nullable=False),
        sa.Column("ronda_id", sa.Integer(), nullable=True),
        sa.Column("actualizado", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("usuario_email"),
    )
    op.create_index("ix_presencias_actualizado", "presencias", ["actualizado"], unique=False)

    op.create_table(
        "rondas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=120), nullable=False),
        sa.Column("snapshot", sa.String(length=200), nullable=False),
        sa.Column("abierta", sa.Boolean(), nullable=False),
        sa.Column("creada", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_rondas_id", "rondas", ["id"], unique=False)

    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sub_oidc", sa.String(length=64), nullable=True),
        sa.Column("email", sa.String(length=200), nullable=False),
        sa.Column("nombre", sa.String(length=200), nullable=False),
        sa.Column("ultimo_acceso", sa.DateTime(timezone=True), nullable=False),
        sa.Column("permisos", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_usuarios_email", "usuarios", ["email"], unique=True)
    op.create_index("ix_usuarios_id", "usuarios", ["id"], unique=False)
    op.create_index("ix_usuarios_sub_oidc", "usuarios", ["sub_oidc"], unique=True)

    op.create_table(
        "aprobaciones",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ronda_id", sa.Integer(), nullable=False),
        sa.Column(
            "tipo",
            sa.Enum(
                "herramienta", "caracteristica", name="tipo_aprobacion", create_constraint=True
            ),
            nullable=False,
        ),
        sa.Column("objetivo_id", sa.String(length=120), nullable=False),
        sa.Column(
            "estado",
            sa.Enum(
                "aprobada",
                "rechazada",
                "pendiente",
                name="estado_aprobacion",
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("comentario", sa.Text(), nullable=False),
        sa.Column("usuario_email", sa.String(length=200), nullable=False),
        sa.Column("usuario_nombre", sa.String(length=200), nullable=False),
        sa.Column("creada", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["ronda_id"], ["rondas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_aprobaciones_id", "aprobaciones", ["id"], unique=False)
    op.create_index("ix_aprobaciones_objetivo_id", "aprobaciones", ["objetivo_id"], unique=False)
    op.create_index("ix_aprobaciones_ronda_id", "aprobaciones", ["ronda_id"], unique=False)

    op.create_table(
        "asignaciones",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ronda_id", sa.Integer(), nullable=False),
        sa.Column("usuario_email", sa.String(length=200), nullable=False),
        sa.Column("seccion_id", sa.String(length=120), nullable=False),
        sa.ForeignKeyConstraint(["ronda_id"], ["rondas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ronda_id", "usuario_email", "seccion_id"),
    )
    op.create_index("ix_asignaciones_id", "asignaciones", ["id"], unique=False)
    op.create_index("ix_asignaciones_ronda_id", "asignaciones", ["ronda_id"], unique=False)
    op.create_index(
        "ix_asignaciones_usuario_email", "asignaciones", ["usuario_email"], unique=False
    )

    op.create_table(
        "decisiones",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ronda_id", sa.Integer(), nullable=False),
        sa.Column("herramienta_id", sa.String(length=120), nullable=False),
        sa.Column(
            "decision",
            sa.Enum(
                "desplegar",
                "desplegar_con_aviso",
                "aplazar",
                "pendiente",
                name="decision",
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("motivo", sa.Text(), nullable=False),
        sa.Column("decidido_por", sa.String(length=200), nullable=False),
        sa.Column("actualizado", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["ronda_id"], ["rondas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ronda_id", "herramienta_id"),
    )
    op.create_index("ix_decisiones_herramienta_id", "decisiones", ["herramienta_id"], unique=False)
    op.create_index("ix_decisiones_id", "decisiones", ["id"], unique=False)
    op.create_index("ix_decisiones_ronda_id", "decisiones", ["ronda_id"], unique=False)

    op.create_table(
        "fallas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ronda_id", sa.Integer(), nullable=False),
        sa.Column("caso_id", sa.String(length=60), nullable=False),
        sa.Column("usuario_email", sa.String(length=200), nullable=False),
        sa.Column("paso", sa.Integer(), nullable=True),
        sa.Column("seccion_id", sa.String(length=120), nullable=True),
        sa.Column("tipo", sa.String(length=10), server_default="falla", nullable=False),
        sa.Column("obtenido", sa.Text(), nullable=False),
        sa.Column(
            "reproducible",
            sa.Enum("siempre", "a_veces", "una_vez", name="reproducible", create_constraint=True),
            nullable=False,
        ),
        sa.Column(
            "severidad",
            sa.Enum("critica", "alta", "media", "baja", name="severidad", create_constraint=True),
            nullable=False,
        ),
        sa.Column("navegador", sa.String(length=400), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("version_visible", sa.String(length=120), nullable=False),
        sa.Column("creada", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "estado",
            sa.Enum(
                "nueva",
                "en_curso",
                "lista_para_revalidar",
                "cerrada",
                name="estado_falla",
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("nota_resolucion", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["ronda_id"], ["rondas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_fallas_caso_id", "fallas", ["caso_id"], unique=False)
    op.create_index("ix_fallas_estado", "fallas", ["estado"], unique=False)
    op.create_index("ix_fallas_id", "fallas", ["id"], unique=False)
    op.create_index("ix_fallas_ronda_id", "fallas", ["ronda_id"], unique=False)
    op.create_index("ix_fallas_seccion_id", "fallas", ["seccion_id"], unique=False)
    op.create_index("ix_fallas_severidad", "fallas", ["severidad"], unique=False)
    op.create_index("ix_fallas_tipo", "fallas", ["tipo"], unique=False)
    op.create_index("ix_fallas_usuario_email", "fallas", ["usuario_email"], unique=False)

    op.create_table(
        "resultados",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ronda_id", sa.Integer(), nullable=False),
        sa.Column("caso_id", sa.String(length=60), nullable=False),
        sa.Column("usuario_email", sa.String(length=200), nullable=False),
        sa.Column(
            "estado",
            sa.Enum(
                "pendiente",
                "pasa",
                "falla",
                "no_pude",
                name="estado_resultado",
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("pasos_marcados", sa.JSON(), nullable=False),
        sa.Column("comentario", sa.Text(), nullable=True),
        sa.Column("actualizado", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["ronda_id"], ["rondas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ronda_id", "caso_id", "usuario_email"),
    )
    op.create_index("ix_resultados_caso_id", "resultados", ["caso_id"], unique=False)
    op.create_index("ix_resultados_id", "resultados", ["id"], unique=False)
    op.create_index("ix_resultados_ronda_id", "resultados", ["ronda_id"], unique=False)
    op.create_index("ix_resultados_usuario_email", "resultados", ["usuario_email"], unique=False)

    op.create_table(
        "sesiones",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("access_token", sa.Text(), nullable=False),
        sa.Column("refresh_token", sa.Text(), nullable=True),
        sa.Column("access_expira", sa.DateTime(timezone=True), nullable=False),
        sa.Column("permisos_locales", sa.JSON(), nullable=True),
        sa.Column("renovando_hasta", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sesiones_usuario_id", "sesiones", ["usuario_id"], unique=False)

    op.create_table(
        "avisos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_email", sa.String(length=200), nullable=False),
        sa.Column("titulo", sa.String(length=200), nullable=False),
        sa.Column("mensaje", sa.Text(), nullable=False),
        sa.Column("falla_id", sa.Integer(), nullable=True),
        sa.Column("caso_id", sa.String(length=60), nullable=True),
        sa.Column("autor_email", sa.String(length=200), nullable=False),
        sa.Column("autor_nombre", sa.String(length=200), nullable=False),
        sa.Column("creado", sa.DateTime(timezone=True), nullable=False),
        sa.Column("leido", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["falla_id"], ["fallas.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_avisos_creado", "avisos", ["creado"], unique=False)
    op.create_index("ix_avisos_falla_id", "avisos", ["falla_id"], unique=False)
    op.create_index("ix_avisos_id", "avisos", ["id"], unique=False)
    op.create_index("ix_avisos_usuario_email", "avisos", ["usuario_email"], unique=False)

    op.create_table(
        "evidencias",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("falla_id", sa.Integer(), nullable=False),
        sa.Column("ruta", sa.String(length=300), nullable=False),
        sa.Column("mime", sa.String(length=40), nullable=False),
        sa.Column("creada", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["falla_id"], ["fallas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_evidencias_falla_id", "evidencias", ["falla_id"], unique=False)
    op.create_index("ix_evidencias_id", "evidencias", ["id"], unique=False)


def downgrade() -> None:
    for tabla in reversed(TABLAS):
        op.drop_table(tabla)
