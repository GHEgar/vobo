"""presencia con navegador, dispositivo, pantalla y duracion

Revision ID: 0006
Revises: 0005
Create Date: 2026-10-16 12:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: str | Sequence[str] | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("presencias", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("navegador", sa.String(length=80), nullable=False, server_default="")
        )
        batch_op.add_column(
            sa.Column("agente", sa.String(length=300), nullable=False, server_default="")
        )
        batch_op.add_column(
            sa.Column(
                "dispositivo", sa.String(length=10), nullable=False, server_default="escritorio"
            )
        )
        batch_op.add_column(sa.Column("pantalla", sa.String(length=11), nullable=True))
        batch_op.add_column(sa.Column("desde", sa.DateTime(timezone=True), nullable=True))
    op.execute(sa.text("UPDATE presencias SET desde = actualizado"))


def downgrade() -> None:
    with op.batch_alter_table("presencias", schema=None) as batch_op:
        batch_op.drop_column("desde")
        batch_op.drop_column("pantalla")
        batch_op.drop_column("dispositivo")
        batch_op.drop_column("agente")
        batch_op.drop_column("navegador")
