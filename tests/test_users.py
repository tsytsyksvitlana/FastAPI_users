import json
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from web_app.auth import utils

pytestmark = pytest.mark.anyio


@pytest.fixture
async def mock_redis():
    with patch("web_app.auth.router.redis", autospec=True) as mock_redis:
        mock_redis.exists = AsyncMock(return_value=0)
        mock_redis.get = AsyncMock(
            return_value=json.dumps(
                {
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "testuserrouter1@example.com",
                    "password": utils.hash_password("dshbhjHH03/").decode(
                        "utf-8"
                    ),
                    "balance": 10,
                }
            )
        )
        yield mock_redis


@pytest.fixture
async def test_user_token(client, db_session, mock_redis):
    response = await client.post(
        "/api/v1/auth/login/",
        data={
            "email": "testuserrouter1@example.com",
            "password": "dshbhjHH03/",
        },
    )
    assert response.status_code == 200
    return response.json().get("access_token")


test_get_users_cases = [
    ({}, 200),
    ({"first_name": "John"}, 200),
    ({"sort_by": "balance", "sort_order": "desc"}, 200),
    ({"sort_by": "invalid_field"}, 400),
    ({"sort_order": "invalid_order"}, 400),
]


@pytest.mark.parametrize("params, expected_status", test_get_users_cases)
async def test_get_users(
    client, db_session: AsyncSession, params: dict, expected_status: int
):
    response = await client.get("/api/v1/users/", params=params)
    assert response.status_code == expected_status

    if expected_status == 200:
        assert isinstance(response.json(), list)
        if "first_name" in params:
            assert all(
                user["first_name"] == params["first_name"]
                for user in response.json()
            )
    elif expected_status == 400:
        error_detail = response.json().get("detail", "")
        if "sort_by" in params and params["sort_by"] == "invalid_field":
            assert error_detail == "Invalid sort_by field: invalid_field"
        elif "sort_order" in params and params["sort_order"] == "invalid_order":
            assert error_detail == "Invalid sort_order field: invalid_order"


async def test_retrieve_profiles(client, db_session: AsyncSession):
    response = await client.get("/api/v1/users/profile/")
    assert response.status_code == 200
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


# test_get_balance_cases = [
#     (1, 200),
#     (999, 404),
# ]
#
#
# @pytest.mark.parametrize(
#     "user_id, expected_status", test_get_balance_cases
# )
# async def test_get_balance(
#     client, user_id: int, expected_status: int, test_user_token: str
# ):
#     response = await client.get(
#         f"/api/v1/users/{user_id}/balance/",
#         headers={"Authorization": f"Bearer {test_user_token}"},
#     )
#     assert response.status_code == expected_status
#     if expected_status == 200:
#         assert isinstance(response.json(), int)
