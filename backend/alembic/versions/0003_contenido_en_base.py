"""contenido en base

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-15 22:54:12.841491
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | Sequence[str] | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "contenido_media",
        sa.Column("procedimiento_id", sa.String(length=120), nullable=False),
        sa.Column("archivo", sa.String(length=200), nullable=False),
        sa.Column("mime", sa.String(length=60), nullable=False),
        sa.Column("tamano", sa.Integer(), nullable=False),
        sa.Column("huella", sa.String(length=64), nullable=False),
        sa.Column("subido", sa.DateTime(timezone=True), nullable=False),
        sa.Column("autor_email", sa.String(length=200), nullable=False),
        sa.PrimaryKeyConstraint("procedimiento_id"),
    )
    op.create_table(
        "contenido_procedimientos",
        sa.Column("id", sa.String(length=120), nullable=False),
        sa.Column("orden", sa.Integer(), nullable=False),
        sa.Column("datos", sa.JSON(), nullable=False),
        sa.Column("actualizado", sa.DateTime(timezone=True), nullable=False),
        sa.Column("autor_email", sa.String(length=200), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "contenido_secciones",
        sa.Column("id", sa.String(length=120), nullable=False),
        sa.Column("orden", sa.Integer(), nullable=False),
        sa.Column("datos", sa.JSON(), nullable=False),
        sa.Column("actualizado", sa.DateTime(timezone=True), nullable=False),
        sa.Column("autor_email", sa.String(length=200), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "contenido_versiones",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(length=20), nullable=False),
        sa.Column("objeto_id", sa.String(length=120), nullable=False),
        sa.Column("accion", sa.String(length=20), nullable=False),
        sa.Column("datos", sa.JSON(), nullable=True),
        sa.Column("autor_email", sa.String(length=200), nullable=False),
        sa.Column("creado", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("contenido_versiones", schema=None) as batch_op:
        batch_op.create_index("ix_contenido_versiones_objeto", ["tipo", "objeto_id"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("contenido_versiones", schema=None) as batch_op:
        batch_op.drop_index("ix_contenido_versiones_objeto")

    op.drop_table("contenido_versiones")
    op.drop_table("contenido_secciones")
    op.drop_table("contenido_procedimientos")
    op.drop_table("contenido_media")
