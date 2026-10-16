"""roles y cuentas propias

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-15 22:34:04.486481
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | Sequence[str] | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ROLES_SISTEMA = (
    {
        "clave": "validador",
        "nombre": "Validador",
        "descripcion": "Ejecuta los casos que tiene asignados y reporta fallas.",
        "permisos": ["validacion.casos.ejecutar"],
    },
    {
        "clave": "coordinacion",
        "nombre": "Coordinación",
        "descripcion": "Organiza las rondas, sigue el tablero y gestiona las fallas.",
        "permisos": [
            "validacion.casos.ejecutar",
            "validacion.fallas.gestionar",
            "validacion.tablero.ver",
        ],
    },
    {
        "clave": "aprobacion",
        "nombre": "Aprobación",
        "descripcion": "Aprueba o rechaza herramientas y características.",
        "permisos": ["validacion.herramientas.aprobar"],
    },
    {
        "clave": "administracion",
        "nombre": "Administración",
        "descripcion": "Administra personas y roles; incluye todos los demás permisos.",
        "permisos": ["validacion.admin"],
    },
)


def upgrade() -> None:
    op.create_table(
        "intentos_entrada",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("clave", sa.String(length=260), nullable=False),
        sa.Column("momento", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("intentos_entrada", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_intentos_entrada_clave"), ["clave"], unique=False)
        batch_op.create_index(batch_op.f("ix_intentos_entrada_momento"), ["momento"], unique=False)

    op.create_table(
        "invitaciones",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("email", sa.String(length=200), nullable=False),
        sa.Column("roles", sa.JSON(), nullable=False),
        sa.Column("creada_por", sa.String(length=200), nullable=False),
        sa.Column("creada", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expira", sa.DateTime(timezone=True), nullable=False),
        sa.Column("usada", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    with op.batch_alter_table("invitaciones", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_invitaciones_email"), ["email"], unique=False)

    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("clave", sa.String(length=60), nullable=False),
        sa.Column("nombre", sa.String(length=120), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=False),
        sa.Column("permisos", sa.JSON(), nullable=False),
        sa.Column("sistema", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("roles", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_roles_clave"), ["clave"], unique=True)

    op.create_table(
        "cuentas",
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("hash", sa.String(length=200), nullable=False),
        sa.Column("activa", sa.Boolean(), nullable=False),
        sa.Column("creada", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ultimo_cambio", sa.DateTime(timezone=True), nullable=False),
        sa.Column("debe_cambiar", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("usuario_id"),
    )
    op.create_table(
        "restablecimientos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("creado_por", sa.String(length=200), nullable=False),
        sa.Column("creado", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expira", sa.DateTime(timezone=True), nullable=False),
        sa.Column("usado", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    with op.batch_alter_table("restablecimientos", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_restablecimientos_usuario_id"), ["usuario_id"], unique=False
        )

    op.create_table(
        "usuario_roles",
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("rol_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["rol_id"], ["roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("usuario_id", "rol_id"),
    )
    with op.batch_alter_table("usuario_roles", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_usuario_roles_usuario_id"), ["usuario_id"], unique=False
        )

    with op.batch_alter_table("sesiones", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("origen", sa.String(length=10), server_default="oidc", nullable=False)
        )
    op.execute("UPDATE sesiones SET origen = 'local' WHERE permisos_locales IS NOT NULL")

    roles = sa.table(
        "roles",
        sa.column("clave", sa.String),
        sa.column("nombre", sa.String),
        sa.column("descripcion", sa.Text),
        sa.column("permisos", sa.JSON),
        sa.column("sistema", sa.Boolean),
    )
    op.bulk_insert(roles, [{**rol, "sistema": True} for rol in ROLES_SISTEMA])


def downgrade() -> None:
    with op.batch_alter_table("sesiones", schema=None) as batch_op:
        batch_op.drop_column("origen")

    with op.batch_alter_table("usuario_roles", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_usuario_roles_usuario_id"))

    op.drop_table("usuario_roles")
    with op.batch_alter_table("restablecimientos", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_restablecimientos_usuario_id"))

    op.drop_table("restablecimientos")
    op.drop_table("cuentas")
    with op.batch_alter_table("roles", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_roles_clave"))

    op.drop_table("roles")
    with op.batch_alter_table("invitaciones", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_invitaciones_email"))

    op.drop_table("invitaciones")
    with op.batch_alter_table("intentos_entrada", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_intentos_entrada_momento"))
        batch_op.drop_index(batch_op.f("ix_intentos_entrada_clave"))

    op.drop_table("intentos_entrada")
