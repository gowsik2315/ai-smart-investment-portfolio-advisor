"""
Database Initialization Script
Run this script to initialize the database with tables.

Output is deliberately plain ASCII. Emoji in `print()` raise
UnicodeEncodeError on Windows whenever stdout is not UTF-8 — which is
the case any time this script's output is piped or redirected to a file.

Note that the table list below is printed from a hardcoded string and
does not reflect the full schema; `create_all` creates every table
registered on `Base.metadata`, which is more than the six named here.
Prefer `alembic upgrade head` for schema changes.
"""

from app.core.database import engine, Base

# Imported for its side effect: app.models.__init__ imports every model
# module, which is what registers the tables on Base.metadata. Without
# this, create_all() would find nothing to create.
import app.models  # noqa: F401


def init_db():
    """Initialize database tables"""
    print("Initializing database...")
    print(f"Database URL: {engine.url}")

    try:
        # Create all tables registered on Base.metadata
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully.")

        print("\nCreated tables:")
        for table_name in sorted(Base.metadata.tables):
            print(f"  - {table_name}")

    except Exception as e:
        print(f"ERROR creating database tables: {e}")
        raise


if __name__ == "__main__":
    init_db()
