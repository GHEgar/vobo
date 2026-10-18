"""historial de resultados y cierre de rondas

Revision ID: 0007
Revises: 0006
Create Date: 2026-10-18 09:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0007"
down_revision: str | Sequence[str] | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "resultados_historial",
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
        sa.Column("paso", sa.Integer(), nullable=True),
        sa.Column(
            "accion",
            sa.Enum(
                "crear",
                "marcar",
                "cambiar",
                "limpiar",
                "paso",
                name="accion_historial",
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("creado", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["ronda_id"], ["rondas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("resultados_historial", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_resultados_historial_caso_id"), ["caso_id"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_resultados_historial_creado"), ["creado"], unique=False
        )
        batch_op.create_index(batch_op.f("ix_resultados_historial_id"), ["id"], unique=False)
        batch_op.create_index(
            batch_op.f("ix_resultados_historial_ronda_id"), ["ronda_id"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_resultados_historial_usuario_email"), ["usuario_email"], unique=False
        )

    with op.batch_alter_table("rondas", schema=None) as batch_op:
        batch_op.add_column(sa.Column("cerrada_en", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("rondas", schema=None) as batch_op:
        batch_op.drop_column("cerrada_en")

    with op.batch_alter_table("resultados_historial", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_resultados_historial_usuario_email"))
        batch_op.drop_index(batch_op.f("ix_resultados_historial_ronda_id"))
        batch_op.drop_index(batch_op.f("ix_resultados_historial_id"))
        batch_op.drop_index(batch_op.f("ix_resultados_historial_creado"))
        batch_op.drop_index(batch_op.f("ix_resultados_historial_caso_id"))

    op.drop_table("resultados_historial")
