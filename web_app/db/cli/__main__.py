import argparse
import asyncio
import json
import logging
from datetime import datetime

from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from web_app.auth import utils
from web_app.db.config import settings
from web_app.models.base import Base
from web_app.models.user import User

logger = logging.getLogger(__name__)

engine = create_async_engine(settings.url, echo=settings.echo)
AsyncSessionLocal = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


def create_db() -> None:
    """
    Create the database and all tables.
    """
    logger.info("Creating database...")

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

    async def async_drop():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    asyncio.run(async_drop())
    logger.info("Database dropped.")


def populate_db(file_path: str) -> None:
    """
    Populate the database with initial data from a JSON file.
    """
    logger.info("Populating database with sample data...")

    async def async_populate():
        with open(file_path, "r") as f:
            data = json.load(f)

        async with AsyncSessionLocal() as session:
            async with session.begin():
                users = [
                    User(
                        first_name=user["first_name"],
                        last_name=user["last_name"],
                        email=user["email"],
                        password=utils.hash_password(user["password"]).decode(
                            "utf-8"
                        ),
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                        last_activity_at=datetime.now(),
                        balance=user["balance"],
                        block_status=user["block_status"],
                    )
                    for user in data.get("users", [])
                ]
                session.add_all(users)
                await session.commit()

    asyncio.run(async_populate())
    logger.info("Database populated with sample data.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage the database.")
    parser.add_argument(
        "command",
        type=str,
        choices=["create", "drop", "migrate", "populate"],
        help="Command to run: create, drop, migrate, or populate",
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Path to the JSON file for populating the database",
        required=False,
    )

    args = parser.parse_args()

    if args.command == "create":
        create_db()
    elif args.command == "drop":
        drop_db()
    elif args.command == "migrate":
        run_migrations()
    elif args.command == "populate":
        if not args.file:
            logger.error(
                "JSON file path is required for populating the database."
            )
        else:
            populate_db(args.file)
    else:
        logger.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
