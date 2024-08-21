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

from web_app.db.config import settings
from web_app.db.db_helper import DatabaseHelper
from web_app.main import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TEST_URL = settings.test_db_url()

db_helper = DatabaseHelper(url=TEST_URL, echo=settings.echo)


@pytest.fixture(scope="module")
async def setup_test_db():
    logger.info("Setting up the test database...")

    engine = create_async_engine(TEST_URL, echo=False)

    async with engine.connect() as conn:
        await conn.execute(text("COMMIT"))
        await conn.execute(text("DROP DATABASE IF EXISTS testdb"))
        await conn.execute(text("COMMIT"))
        await conn.execute(text("CREATE DATABASE testdb"))

    alembic_cfg = Config("web_app/alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", TEST_URL)
    alembic_cfg.set_main_option("script_location", "web_app/migrations")
    command.upgrade(alembic_cfg, "head")
    logger.info("Database migrations applied.")

    yield

    async with engine.connect() as conn:
        await conn.execute(text("COMMIT"))
        await conn.execute(text("DROP DATABASE IF EXISTS testdb"))

    await engine.dispose()
    logger.info("Test database dropped.")


@pytest.fixture(scope="module")
async def db_session(setup_test_db) -> AsyncSession:
    engine = create_async_engine(TEST_URL, echo=False)
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
