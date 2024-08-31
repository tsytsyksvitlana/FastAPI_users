import argparse
import asyncio
import logging

from alembic.config import Config
from sqlalchemy.ext.asyncio import create_async_engine

from web_app.db.config import settings
from web_app.models.base import Base

logger = logging.getLogger(__name__)


def create_db() -> None:
    """
    Create the database and all tables.
    """
    logger.info("Creating database...")
    engine = create_async_engine(settings.url, echo=settings.echo)

    async def async_create():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(async_create())
    logger.info("Database created.")


def run_migrations() -> None:
    """
    Run Alembic migrations.
    """
    logger.info("Running migrations...")
    alembic_cfg = Config("web_app/alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.url)
    alembic_cfg.set_main_option("script_location", "web_app/migrations")

    from alembic import command

    command.upgrade(alembic_cfg, "head")
    logger.info("Migrations completed.")


def drop_db() -> None:
    """
    Drop the database and all tables.
    """
    logger.info("Dropping database...")
    engine = create_async_engine(settings.url, echo=settings.echo)

    async def async_drop():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    asyncio.run(async_drop())
    logger.info("Database dropped.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage the database.")
    parser.add_argument(
        "command",
        type=str,
        choices=["create", "drop", "migrate"],
        help="Command to run: create, drop, or migrate",
    )

    args = parser.parse_args()

    if args.command == "create":
        create_db()
    elif args.command == "drop":
        drop_db()
    elif args.command == "migrate":
        run_migrations()
    else:
        logger.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
