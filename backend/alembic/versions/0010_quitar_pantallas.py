"""quitar las pantallas de avance

Revision ID: 0010
Revises: 0009
Create Date: 2026-10-19 12:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0010"
down_revision: str | Sequence[str] | None = "0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("pantallas", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_pantallas_token_hash"))

    op.drop_table("pantallas")


def downgrade() -> None:
    op.create_table(
        "pantallas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=120), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("vistas", sa.JSON(), nullable=False),
        sa.Column("segundos", sa.Integer(), nullable=False),
        sa.Column("proyectos", sa.JSON(), nullable=False),
        sa.Column("activa", sa.Boolean(), nullable=False),
        sa.Column("creada", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ultimo_uso", sa.DateTime(timezone=True), nullable=True),
        sa.Column("autor_email", sa.String(length=200), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("pantallas", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_pantallas_token_hash"), ["token_hash"], unique=True)
