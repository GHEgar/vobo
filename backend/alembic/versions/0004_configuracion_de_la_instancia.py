"""configuracion de la instancia

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-15 23:20:24.172788
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: str | Sequence[str] | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "configuracion",
        sa.Column("clave", sa.String(length=40), nullable=False),
        sa.Column("valor", sa.JSON(), nullable=False),
        sa.Column("actualizado", sa.DateTime(timezone=True), nullable=False),
        sa.Column("autor_email", sa.String(length=200), nullable=False),
        sa.PrimaryKeyConstraint("clave"),
    )


def downgrade() -> None:
    op.drop_table("configuracion")
