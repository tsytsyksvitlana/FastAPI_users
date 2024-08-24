import logging

import pytest
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from web_app.db.config import settings
from web_app.main import app
from web_app.models.base import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def override_settings():
    settings.url = settings.test_db_url
    yield


@pytest.fixture(scope="module")
async def setup_test_db(override_settings):
    logger.info("Setting up the test database...")

    engine = create_async_engine(settings.url, echo=False)
    async_session = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database tables created.")

    alembic_cfg = Config("web_app/alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.url)
    alembic_cfg.set_main_option("script_location", "web_app/migrations")
    logger.info("Alembic config loaded.")
    command.upgrade(alembic_cfg, "head")
    logger.info("Database migrations applied.")

    yield async_session

    logger.info("Tearing down the test database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()
    logger.info("Test database dropped.")


@pytest.fixture(scope="function")
async def db_session(setup_test_db) -> AsyncSession:
    async_session = setup_test_db

    async with async_session() as session:
        async with session.begin():
            for table in reversed(Base.metadata.sorted_tables):
                await session.execute(table.delete())

        yield session


@pytest.fixture(scope="module")
async def client():
    logger.info("Creating HTTP client...")
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://localhost:8000"
    ) as ac:
        yield ac
    logger.info("HTTP client closed.")
