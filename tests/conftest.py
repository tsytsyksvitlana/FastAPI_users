import logging

import pytest
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from web_app.db.config import Settings, settings
from web_app.db.db_helper import DatabaseHelper
from web_app.main import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

test_settings = Settings(".env.test")
db_helper = DatabaseHelper(url=settings.url(), echo=settings.echo)


@pytest.fixture(scope="module")
async def setup_test_db():
    logger.info("Setting up the test database...")

    # Create an engine to the default database
    default_engine = create_async_engine(settings.url(), echo=False)
    test_db_url = test_settings.url()

    # Connect to the default database
    async with default_engine.connect() as conn:
        # Set isolation level and execute commands
        await conn.execution_options(isolation_level="AUTOCOMMIT")
        await conn.execute(text("DROP DATABASE IF EXISTS test_db;"))
        await conn.execute(text("CREATE DATABASE test_db;"))

    await default_engine.dispose()

    # Create the engine for the test database
    engine = create_async_engine(test_db_url, echo=False)

    # Apply migrations to the test database
    alembic_cfg = Config("web_app/alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", test_db_url)
    alembic_cfg.set_main_option("script_location", "web_app/migrations")
    command.upgrade(alembic_cfg, "head")
    logger.info("Database migrations applied.")

    yield
    # Drop the test database after tests
    async with default_engine.connect() as conn:
        # Set isolation level and execute command
        await conn.execution_options(isolation_level="AUTOCOMMIT")
        await conn.execute(text("DROP DATABASE IF EXISTS test_db;"))
    logger.info("Test database dropped.")

    await engine.dispose()


@pytest.fixture(scope="module")
async def db_session(setup_test_db) -> AsyncSession:
    logger.info("Creating a database session...")
    async with db_helper.session_getter() as session:
        yield session
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
