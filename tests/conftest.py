import logging

import pytest
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from web_app.db.config import Settings, settings
from web_app.db.db_helper import DatabaseHelper
from web_app.main import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

test_settings = Settings(".env.test")
db_helper = DatabaseHelper(url=test_settings.url(), echo=test_settings.echo)


@pytest.fixture(scope="module")
async def setup_test_db():
    logger.info("Setting up the test database...")

    default_engine = create_async_engine(settings.url(), echo=False)
    test_db_url = test_settings.url()

    async with default_engine.connect() as conn:
        await conn.execute(
            text("COMMIT")
        )  # ensure the connection is in autocommit mode
        await conn.execute(text("DROP DATABASE IF EXISTS test_db"))
        await conn.execute(text("CREATE DATABASE test_db"))

    await default_engine.dispose()

    engine = create_async_engine(test_db_url, echo=False)

    alembic_cfg = Config("web_app/alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", test_db_url)
    alembic_cfg.set_main_option("script_location", "web_app/migrations")
    command.upgrade(alembic_cfg, "head")
    logger.info("Database migrations applied.")

    yield  # This is where the testing happens

    async with default_engine.connect() as conn:
        await conn.execute(
            text("COMMIT")
        )  # ensure the connection is in autocommit mode
        await conn.execute(text("DROP DATABASE IF EXISTS test_db"))
    logger.info("Test database dropped.")

    await engine.dispose()


@pytest.fixture(scope="module")
async def db_session(setup_test_db) -> AsyncSession:
    engine = create_async_engine(test_settings.url(), echo=False)
    async_session = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    async with async_session() as session:
        yield session

    await engine.dispose()
    logger.info("Database session closed.")


@pytest.fixture(scope="module")
async def client():
    logger.info("Creating HTTP client...")
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://localhost:8000"
    ) as ac:
        yield ac
    logger.info("HTTP client closed.")
