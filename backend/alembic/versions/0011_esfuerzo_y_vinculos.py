"""esfuerzo estimado y vínculos entre fallas y comentarios

Revision ID: 0011
Revises: 0010
Create Date: 2026-10-19 18:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0011"
down_revision: str | Sequence[str] | None = "0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLAS = ("fallas", "comentarios_seguimiento")
COLUMNAS = ("principal_id", "principal_objeto", "esfuerzo_horas")
ACCIONES = ("respuesta", "estado", "plazo", "nota")
NUEVAS = ("esfuerzo", "vinculo")
TEMPORAL = "_seguimiento_nueva"
COPIADAS = "id, objeto, objeto_id, autor_email, accion, texto, anterior, nuevo, creado"


def _indice(tabla: str) -> str:
    return f"ix_{tabla}_principal"


def _recrear_seguimiento(acciones: Sequence[str]) -> None:
    op.create_table(
        TEMPORAL,
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "objeto",
            sa.Enum("falla", "comentario", name="objeto_seguimiento", create_constraint=True),
            nullable=False,
        ),
        sa.Column("objeto_id", sa.Integer(), nullable=False),
        sa.Column("autor_email", sa.String(length=200), nullable=False),
        sa.Column(
            "accion",
            sa.Enum(*acciones, name="accion_seguimiento", create_constraint=True),
            nullable=False,
        ),
        sa.Column("texto", sa.Text(), nullable=False),
        sa.Column("anterior", sa.String(length=40), nullable=True),
        sa.Column("nuevo", sa.String(length=40), nullable=True),
        sa.Column("creado", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute(f"INSERT INTO {TEMPORAL} ({COPIADAS}) SELECT {COPIADAS} FROM seguimiento")
    op.drop_table("seguimiento")
    op.rename_table(TEMPORAL, "seguimiento")
    op.create_index("ix_seguimiento_creado", "seguimiento", ["creado"], unique=False)
    op.create_index("ix_seguimiento_id", "seguimiento", ["id"], unique=False)
    op.create_index("ix_seguimiento_objeto", "seguimiento", ["objeto", "objeto_id"], unique=False)


def upgrade() -> None:
    for tabla in TABLAS:
        op.add_column(tabla, sa.Column("esfuerzo_horas", sa.Float(), nullable=True))
        op.add_column(tabla, sa.Column("principal_objeto", sa.String(length=10), nullable=True))
        op.add_column(tabla, sa.Column("principal_id", sa.Integer(), nullable=True))
        op.create_index(_indice(tabla), tabla, ["principal_objeto", "principal_id"], unique=False)
    _recrear_seguimiento((*ACCIONES, *NUEVAS))


def downgrade() -> None:
    nuevas = ", ".join(f"'{a}'" for a in NUEVAS)
    op.execute(f"DELETE FROM seguimiento WHERE accion IN ({nuevas})")
    _recrear_seguimiento(ACCIONES)
    for tabla in TABLAS:
        op.drop_index(_indice(tabla), table_name=tabla)
        for columna in COLUMNAS:
            op.execute(f"ALTER TABLE {tabla} DROP COLUMN {columna}")
