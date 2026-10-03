"""baseline — schema as it existed before Alembic was adopted

Revision ID: 0001
Revises:
Create Date: 2026-10-03

This revision is intentionally a no-op.

The project created its tables with `Base.metadata.create_all()` at
application startup and had no migration history. Rather than invent a
retroactive CREATE TABLE history that no existing database ever ran,
this revision marks the pre-Alembic state as the starting point. Running
it against an existing database changes nothing; every later revision
describes a real, incremental change from here.

Table creation for a brand-new database still happens via
`create_all()` in `app/main.py`'s lifespan handler. New *changes* from
this point forward belong in migrations.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """No-op: baseline marker for the pre-Alembic schema."""
    pass


def downgrade() -> None:
    """No-op: there is nothing before the baseline."""
    pass
