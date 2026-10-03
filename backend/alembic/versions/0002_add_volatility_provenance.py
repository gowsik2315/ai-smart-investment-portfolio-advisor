"""add volatility provenance columns to monte_carlo_simulations

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-03

Adds the columns that record where a simulation's volatility came from,
so an ML-driven run can be distinguished from a hand-entered one after
the fact:

    volatility_source          'manual' | 'ml_predicted' | 'historical_fallback'
    predicted_volatility       raw model output, retained even if overridden
    volatility_model_version   which model artifact produced it
    volatility_ticker          the instrument forecast for
    random_seed                seed used, so a stored run can be reproduced

Each add is guarded by an inspection of the live table. A database that
was created by `create_all()` after these columns were added to the model
already has them, and an unguarded ADD COLUMN would fail there.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE = "monte_carlo_simulations"

# (name, type factory). A fresh Column is built per use: a Column object
# cannot be attached to two tables, and SQLAlchemy 2.x removed
# Column.copy(), so reusing instances is not an option.
NEW_COLUMNS = [
    ("volatility_source", sa.String),
    ("predicted_volatility", sa.Float),
    ("volatility_model_version", sa.String),
    ("volatility_ticker", sa.String),
    ("random_seed", sa.Integer),
]


def _column(name: str, type_factory) -> sa.Column:
    """Build a fresh nullable Column for `name`."""
    return sa.Column(name, type_factory(), nullable=True)


def _existing_columns() -> set:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if TABLE not in inspector.get_table_names():
        return set()
    return {col["name"] for col in inspector.get_columns(TABLE)}


def upgrade() -> None:
    existing = _existing_columns()

    if not existing:
        # Table absent entirely: a fresh database that has not yet been
        # through create_all(). Nothing to alter.
        return

    for name, type_factory in NEW_COLUMNS:
        if name not in existing:
            op.add_column(TABLE, _column(name, type_factory))

    # Existing rows predate the ML integration, so their volatility was
    # necessarily typed in by hand. Label them rather than leaving NULL,
    # which would be indistinguishable from "unknown".
    op.execute(
        sa.text(
            f"UPDATE {TABLE} SET volatility_source = 'manual' "
            f"WHERE volatility_source IS NULL"
        )
    )


def downgrade() -> None:
    existing = _existing_columns()
    if not existing:
        return

    # SQLite needs batch mode to drop columns; Alembic applies it when
    # render_as_batch is on, but be explicit so downgrade works anywhere.
    with op.batch_alter_table(TABLE) as batch:
        for name, _ in reversed(NEW_COLUMNS):
            if name in existing:
                batch.drop_column(name)
