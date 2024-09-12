from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.bl.auth import utils

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
async def populate_users(db_session: AsyncSession):
    default_users = [
        {
            "first_name": "Alice",
            "last_name": "Wonderland",
            "email": "alice@example.com",
            "role": "user",
            "password": utils.hash_password("dshbhjHH03/").decode("utf-8"),
            "balance": 100,
            "block_status": False,
            "created_at": datetime(2024, 9, 6, 10, 53, 18, 967768),
            "updated_at": datetime(2024, 9, 6, 10, 53, 18, 967841),
            "last_activity_at": datetime(2024, 9, 6, 10, 53, 18, 967864),
            "is_deleted": False,
        },
        {
            "first_name": None,
            "last_name": None,
            "email": "bob@example.com",
            "role": "user",
            "password": utils.hash_password("dshbhjHH03/").decode("utf-8"),
            "balance": 200,
            "block_status": False,
            "created_at": datetime(2024, 9, 6, 10, 53, 18, 967768),
            "updated_at": datetime(2024, 9, 6, 10, 53, 18, 967841),
            "last_activity_at": datetime(2024, 9, 6, 10, 53, 18, 967864),
            "is_deleted": False,
        },
        {
            "first_name": "Charlie",
            "last_name": "Brown",
            "email": "charlie@example.com",
            "role": "user",
            "password": utils.hash_password("dshbhjHH03/").decode("utf-8"),
            "balance": 300,
            "block_status": False,
            "created_at": datetime(2024, 9, 6, 10, 53, 18, 967768),
            "updated_at": datetime(2024, 9, 6, 10, 53, 18, 967841),
            "last_activity_at": datetime(2024, 9, 6, 10, 53, 18, 967864),
            "is_deleted": False,
        },
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


test_get_users_cases = [
    ({}, 200, 3),
    ({"first_name": "Alice"}, 200, 1),
    ({"sort_by": "balance", "sort_order": "desc"}, 200, 3),
    ({"sort_by": "invalid_field"}, 422, 0),
    ({"sort_order": "invalid_order"}, 422, 0),
]


@pytest.mark.parametrize(
    "params, expected_status, expected_count", test_get_users_cases
)
async def test_get_users(
    client,
    populate_users,
    db_session: AsyncSession,
    params: dict,
    expected_status: int,
    expected_count: int,
):
    response = await client.post("/api/v1/users/", json=params)
    assert response.status_code == expected_status

    if expected_status == 200:
        json_response = response.json()
        assert isinstance(json_response, list)
        assert len(json_response) == expected_count
        if "first_name" in params:
            assert all(
                user["first_name"] == params["first_name"]
                for user in json_response
            )
    elif expected_status == 400:
        error_detail = response.json().get("detail", "")
        if "sort_by" in params and params["sort_by"] == "invalid_field":
            assert error_detail == f"Invalid sort_by field: {params['sort_by']}"
        elif "sort_order" in params and params["sort_order"] == "invalid_order":
            res = f"Invalid sort_order field: {params['sort_order']}"
            assert error_detail == res


async def test_retrieve_profiles(
    client, db_session: AsyncSession, populate_users
):
    response = await client.get("/api/v1/users/profile/")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert isinstance(response.json(), list)


async def test_retrieve_profile(client, test_user_token: str):
    response = await client.get(
        "/api/v1/users/profile/me/",
        headers={"Authorization": f"Bearer {test_user_token}"},
    )
    assert response.status_code == 200
    user_profile = response.json()
    assert "first_name" in user_profile
    assert "last_name" in user_profile


test_get_balance_cases = [
    (1, 200),
    (999, 404),
]


@pytest.mark.parametrize("user_id, expected_status", test_get_balance_cases)
async def test_get_balance(
    client, user_id: int, expected_status: int, test_user_token: str
):
    response = await client.get(
        f"/api/v1/users/{user_id}/balance/",
        headers={"Authorization": f"Bearer {test_user_token}"},
    )
    assert response.status_code == expected_status
    if expected_status == 200:
        assert isinstance(response.json(), int)


test_update_profile_cases = [
    ({"first_name": "Jane", "last_name": "Doe"}, 200),
    ({"first_name": "Jane", "last_name": "Doe", "balance": -10}, 422),
    ({"first_name": ""}, 200),
    ({"balance": 10}, 200),
]


@pytest.mark.parametrize(
    "update_data, expected_status", test_update_profile_cases
)
async def test_update_profile(
    client,
    db_session,
    update_data: dict,
    expected_status: int,
    test_user_token: str,
):
    response = await client.put(
        "/api/v1/users/profile/",
        json=update_data,
        headers={"Authorization": f"Bearer {test_user_token}"},
    )
    assert response.status_code == expected_status

    if expected_status == 200:
        updated_user = response.json()
        for field, value in update_data.items():
            if value:
                assert updated_user[field] == value


test_update_balance_cases = [
    (1, {"balance": 100}, 200),
    (999, {"balance": 100}, 404),
    (1, {"balance": -50}, 422),
]


@pytest.mark.parametrize(
    "user_id, update_data, expected_status", test_update_balance_cases
)
async def test_update_balance(
    client,
    user_id: int,
    update_data: dict,
    expected_status: int,
    test_user_token: str,
):
    response = await client.put(
        f"/api/v1/users/{user_id}/balance/",
        json=update_data,
        headers={"Authorization": f"Bearer {test_user_token}"},
    )
    assert response.status_code == expected_status

    if expected_status == 200:
        updated_user = response.json()
        assert updated_user["balance"] == update_data["balance"]
    elif expected_status == 404:
        assert response.json().get("detail") == "User not found"
    elif expected_status == 422:
        assert response.json().get("detail")


test_delete_account_cases = [(1, 204), (999, 404), (2, 404)]


@pytest.mark.parametrize("user_id, expected_status", test_delete_account_cases)
async def test_delete_account(
    client, user_id: int, expected_status: int, test_user_token: str
):
    response = await client.delete(
        f"/api/v1/users/{user_id}/delete/",
        headers={"Authorization": f"Bearer {test_user_token}"},
    )
    assert response.status_code == expected_status
