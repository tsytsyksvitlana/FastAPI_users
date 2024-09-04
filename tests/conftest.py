import logging

import pytest
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from web_app.db.config import settings, test_settings
from web_app.db.db_helper import db_helper
from web_app.main import app
from web_app.models.base import Base
from web_app.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
async def setup_test_db():
    logger.info("Setting up the test database...")
    original_url = settings.url
    settings.url = test_settings.url

    db_helper.engine.url = settings.url
    db_helper.engine = create_async_engine(settings.url, echo=settings.echo)
    db_helper.session_factory = async_sessionmaker(
        bind=db_helper.engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created.")

    alembic_cfg = Config("web_app/alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.url)
    alembic_cfg.set_main_option("script_location", "web_app/migrations")

    yield db_helper.session_factory

    logger.info("Tearing down the test database...")
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await db_helper.dispose()

    settings.url = original_url
    db_helper.engine = create_async_engine(settings.url, echo=settings.echo)
    db_helper.session_factory = async_sessionmaker(
        bind=db_helper.engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    logger.info("Test database dropped and original DatabaseHelper restored.")


@pytest.fixture(scope="module")
async def db_session(setup_test_db) -> AsyncSession:
    async_session = setup_test_db
    async with async_session() as session:
        yield session


@pytest.fixture(scope="function")
async def create_default_users(db_session):
    logger.info("Creating default users...")

    default_users = [
        {
            "first_name": "John",
            "last_name": "Doe",
            "email": "testuserrouter1@example.com",
            "password": "dshbhjHH03/",
        },
        {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "testuserrouter2@example.com",
            "password": "wqjdb*939/D",
        },
        {"email": "testuserrouter3@example.com", "password": "shbdHHHS776w/"},
        {
            "first_name": "Bob",
            "last_name": "Brown",
            "email": "testuserrouter4@example.com",
            "password": "365e4bsdhb/HGFS",
        },
    ]

    try:
        for user_data in default_users:
            logger.info(f"Adding user: {user_data['email']} to the database.")
            user = User(**user_data)
            db_session.add(user)

        await db_session.commit()
        logger.info("Users committed to the database.")
    except Exception as e:
        logger.error(f"Error while creating users: {e}")
        await db_session.rollback()
        raise

    return default_users


@pytest.fixture(scope="module")
async def client():
    logger.info("Creating HTTP client...")
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://localhost:8000"
    ) as ac:
        yield ac
    logger.info("HTTP client closed.")


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"
