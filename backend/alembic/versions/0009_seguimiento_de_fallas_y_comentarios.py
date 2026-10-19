"""seguimiento de fallas y comentarios

Revision ID: 0009
Revises: 0008
Create Date: 2026-10-19 09:00:00.000000
"""

import json
from collections.abc import Iterator, Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0009"
down_revision: str | Sequence[str] | None = "0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

PASO_NO_PUDE = -1
COLUMNAS_FALLA = ("resuelta_por", "resuelta_en", "plazo_por", "plazo")


def _pasos(valor: object) -> list[object]:
    if isinstance(valor, str):
        try:
            valor = json.loads(valor)
        except ValueError:
            return []
    if not isinstance(valor, list):
        return []
    return [{"paso": p, "estado": "pasa"} if isinstance(p, int) else p for p in valor]


def _comentarios(fila: sa.Row) -> Iterator[tuple[int, str]]:
    for marcado in _pasos(fila.pasos_marcados):
        if not isinstance(marcado, dict) or not isinstance(marcado.get("paso"), int):
            continue
        if (marcado.get("comentario") or "").strip():
            yield marcado["paso"], "paso"
    if fila.estado == "no_pude" and fila.comentario:
        yield PASO_NO_PUDE, "no_pude"


def _sembrar(conexion: sa.Connection) -> None:
    filas = conexion.execute(
        sa.text(
            "SELECT ronda_id, caso_id, usuario_email, estado, pasos_marcados, comentario, "
            "actualizado FROM resultados ORDER BY id"
        )
    )
    vistos: set[tuple] = set()
    nuevas = []
    for fila in filas:
        for paso, tipo in _comentarios(fila):
            clave = (fila.ronda_id, fila.caso_id, fila.usuario_email, paso, tipo)
            if clave in vistos:
                continue
            vistos.add(clave)
            nuevas.append(
                {
                    "ronda_id": fila.ronda_id,
                    "caso_id": fila.caso_id,
                    "usuario_email": fila.usuario_email,
                    "paso": paso,
                    "tipo": tipo,
                    "creado": fila.actualizado,
                }
            )
    if nuevas:
        conexion.execute(
            sa.text(
                "INSERT INTO comentarios_seguimiento "
                "(ronda_id, caso_id, usuario_email, paso, tipo, estado, creado) "
                "VALUES (:ronda_id, :caso_id, :usuario_email, :paso, :tipo, 'nuevo', :creado)"
            ),
            nuevas,
        )


def upgrade() -> None:
    with op.batch_alter_table("fallas", schema=None) as batch_op:
        batch_op.add_column(sa.Column("plazo", sa.Date(), nullable=True))
        batch_op.add_column(sa.Column("plazo_por", sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column("resuelta_en", sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column("resuelta_por", sa.String(length=200), nullable=True))

    op.create_table(
        "comentarios_seguimiento",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ronda_id", sa.Integer(), nullable=False),
        sa.Column("caso_id", sa.String(length=60), nullable=False),
        sa.Column("usuario_email", sa.String(length=200), nullable=False),
        sa.Column("paso", sa.Integer(), nullable=False),
        sa.Column(
            "tipo",
            sa.Enum("paso", "no_pude", name="tipo_comentario", create_constraint=True),
            nullable=False,
        ),
        sa.Column(
            "estado",
            sa.Enum(
                "nuevo", "en_curso", "resuelto", name="estado_comentario", create_constraint=True
            ),
            nullable=False,
        ),
        sa.Column("plazo", sa.Date(), nullable=True),
        sa.Column("plazo_por", sa.String(length=200), nullable=True),
        sa.Column("creado", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resuelto_en", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resuelto_por", sa.String(length=200), nullable=True),
        sa.ForeignKeyConstraint(["ronda_id"], ["rondas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ronda_id", "caso_id", "usuario_email", "paso", "tipo"),
    )
    with op.batch_alter_table("comentarios_seguimiento", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_comentarios_seguimiento_id"), ["id"], unique=False)
        batch_op.create_index(
            batch_op.f("ix_comentarios_seguimiento_ronda_id"), ["ronda_id"], unique=False
        )

    op.create_table(
        "seguimiento",
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
            sa.Enum(
                "respuesta",
                "estado",
                "plazo",
                "nota",
                name="accion_seguimiento",
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("texto", sa.Text(), nullable=False),
        sa.Column("anterior", sa.String(length=40), nullable=True),
        sa.Column("nuevo", sa.String(length=40), nullable=True),
        sa.Column("creado", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("seguimiento", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_seguimiento_creado"), ["creado"], unique=False)
        batch_op.create_index(batch_op.f("ix_seguimiento_id"), ["id"], unique=False)
        batch_op.create_index("ix_seguimiento_objeto", ["objeto", "objeto_id"], unique=False)

    _sembrar(op.get_bind())


def downgrade() -> None:
    with op.batch_alter_table("seguimiento", schema=None) as batch_op:
        batch_op.drop_index("ix_seguimiento_objeto")
        batch_op.drop_index(batch_op.f("ix_seguimiento_id"))
        batch_op.drop_index(batch_op.f("ix_seguimiento_creado"))

    op.drop_table("seguimiento")

    with op.batch_alter_table("comentarios_seguimiento", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_comentarios_seguimiento_ronda_id"))
        batch_op.drop_index(batch_op.f("ix_comentarios_seguimiento_id"))

    op.drop_table("comentarios_seguimiento")

    for columna in COLUMNAS_FALLA:
        op.execute(f"ALTER TABLE fallas DROP COLUMN {columna}")
