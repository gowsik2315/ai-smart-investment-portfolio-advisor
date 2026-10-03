"""
Alembic environment.

Pulls the database URL from application settings rather than alembic.ini
so migrations always target the same database the app uses.

Every model module is imported below. Alembic's autogenerate compares
`Base.metadata` against the live database, and a model that has not been
imported is invisible to it — autogenerate would then cheerfully emit a
migration dropping the table it could not see.
"""

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

from app.core.config import settings
from app.core.database import Base

# ── Import every model so Base.metadata is complete ─────────────────
from app.models import user  # noqa: F401
from app.models import financial_profile  # noqa: F401
from app.models import risk_profile  # noqa: F401
from app.models import portfolio_recommendation  # noqa: F401
from app.models import portfolio  # noqa: F401
from app.models import portfolio_analysis  # noqa: F401
from app.models import diversification_analysis  # noqa: F401
from app.models import monte_carlo_simulation  # noqa: F401
from app.models import sip_plan  # noqa: F401
from app.models import transaction  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Emit SQL to stdout instead of running it."""
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # SQLite cannot ALTER most things in place; batch mode rewrites
        # the table instead, which Alembic handles transparently.
        render_as_batch=settings.DATABASE_URL.startswith("sqlite"),
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live connection."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=settings.DATABASE_URL.startswith("sqlite"),
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
