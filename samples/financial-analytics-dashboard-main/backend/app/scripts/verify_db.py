"""Quick DB sanity check for Alembic version and forecast constraints."""

from __future__ import annotations

from sqlalchemy import create_engine, text

from app.core.config import settings


def main() -> None:
    engine = create_engine(settings.get_database_url())
    with engine.connect() as conn:
        version = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
        print(f"alembic_version: {version}")

        rows = conn.execute(
            text(
                """
                SELECT conname
                FROM pg_constraint
                WHERE conrelid = 'forecasts'::regclass AND contype = 'u'
                ORDER BY conname
                """
            )
        ).fetchall()
        print("forecasts unique constraints:", [r[0] for r in rows])


if __name__ == "__main__":
    main()
