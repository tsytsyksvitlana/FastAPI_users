from unittest.mock import AsyncMock, patch

import pytest

pytestmark = pytest.mark.anyio


@pytest.fixture
async def mock_redis():
    with patch(
        "web_app.api.v1.routers.auth.router.redis", autospec=True
    ) as mock_redis:
        mock_redis.exists = AsyncMock(return_value=0)
        mock_redis.get = AsyncMock(return_value=(""))
        mock_redis.set = AsyncMock(return_value=True)

        yield mock_redis


@pytest.mark.parametrize(
    "email, password, status",
    [
        ("testuser1@example.com", "dSihhd2dy42/S", 201),
        ("testuser3@example.com", "dSi243", 422),
    ],
)
async def test_register_user(client, db_session, email, password, status):
    response = await client.post(
        "/api/v1/auth/register/", json={"email": email, "password": password}
    )
    assert response.status_code == status


async def test_register_user_existing(client, db_session):
    await client.post(
        "/api/v1/auth/register/",
        json={
            "email": "testuserrouter1@example.com",
            "password": "dSihhd2dy42/S",
        },
    )
    response = await client.post(
        "/api/v1/auth/register/",
        json={
            "email": "testuserrouter1@example.com",
            "password": "dSihhd2dy42/S",
        },
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    "current_password, new_password, status",
    [
        ("dshbhjHH03/", "newpassword1/S", 200),
        ("wrongpassword", "newpassword1/S", 401),
        ("somepassword", "newpassword1/S", 401),
    ],
)
async def test_change_password(
    client, db_session, current_password, new_password, status, test_user_token
):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = await client.post(
        "/api/v1/auth/change_password/",
        data={
            "current_password": current_password,
            "new_password": new_password,
        },
        headers=headers,
    )
    assert response.status_code == status


async def test_refresh_token(client, db_session, test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = await client.post("/api/v1/auth/refresh/", headers=headers)
    assert response.status_code == 200


async def test_refresh_token_no_token(client, db_session):
    headers = {"Authorization": f"Bearer {None}"}
    response = await client.post("/api/v1/auth/refresh/", headers=headers)
    assert response.status_code == 401


async def test_logout_user(client, db_session, test_user_token):
    token = test_user_token or "invalid_token"
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = await client.post("/api/v1/auth/logout/", headers=headers)
    assert response.status_code == 200
