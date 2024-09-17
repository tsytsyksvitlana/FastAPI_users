import logging
from datetime import datetime

import pytest
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from web_app.db.config import settings, test_settings
from web_app.db.db_helper import db_helper
from web_app.main import app
from web_app.models.base import Base
from web_app.services.auth import utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="function")
async def setup_test_db_and_teardown():
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


@pytest.fixture(scope="function")
async def db_session(setup_test_db_and_teardown) -> AsyncSession:
    async_session_factory = setup_test_db_and_teardown
    async with async_session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def client():
    logger.info("Creating HTTP client...")
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://localhost:8000"
    ) as ac:
        yield ac
    logger.info("HTTP client closed.")


@pytest.fixture
async def test_user_token(client, db_session, mock_redis):
    existing_user = await db_session.execute(
        text("SELECT id FROM users WHERE email = 'testuserrouter1@example.com'")
    )
    user_id = existing_user.scalar()

    if not user_id:
        await client.post(
            "/api/v1/auth/register/",
            json={
                "first_name": "John",
                "last_name": "Doe",
                "email": "testuserrouter1@example.com",
                "password": "dshbhjHH03/",
            },
        )

    response = await client.post(
        "/api/v1/auth/login/",
        data={
            "email": "testuserrouter1@example.com",
            "password": "dshbhjHH03/",
        },
    )
    assert response.status_code == 200
    return response.json().get("access_token")


@pytest.fixture
async def test_admin_data_users(db_session: AsyncSession):
    default_users = [
        {
            "first_name": "AdminName",
            "last_name": "AdminLastName",
            "email": "admin@example.com",
            "role": "admin",
            "password": utils.hash_password("adminJHHJHS334/").decode("utf-8"),
            "balance": 0,
            "block_status": False,
            "created_at": datetime(2024, 9, 6, 10, 53, 18, 967768),
            "updated_at": datetime(2024, 9, 6, 10, 53, 18, 967841),
            "last_activity_at": datetime(2024, 9, 6, 10, 53, 18, 967864),
            "is_deleted": False,
        }
    ]

    for user_data in default_users:
        await db_session.execute(
            text(
                "INSERT INTO users (first_name, last_name, email, role, "
                "password, balance, block_status, "
                "created_at, updated_at, last_activity_at, is_deleted) "
                "VALUES (:first_name, :last_name, :email, :role, "
                ":password, :balance, :block_status, "
                ":created_at, :updated_at, :last_activity_at, :is_deleted)"
            ),
            user_data,
        )

    await db_session.commit()
    yield


@pytest.fixture
async def test_admin_token(
    client, db_session, test_admin_data_users, mock_redis
):
    response = await client.post(
        "/api/v1/auth/login/",
        data={
            "email": "admin@example.com",
            "password": "adminJHHJHS334/",
        },
    )
    assert response.status_code == 200
    return response.json().get("access_token")


@pytest.fixture(scope="function")
def anyio_backend():
    return "asyncio"
