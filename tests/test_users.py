import pytest

pytestmark = pytest.mark.anyio


@pytest.fixture
async def test_user_token(client, db_session):
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "testuserrouter1@example.com",
            "password": "dshbhjHH03/",
        },
    )
    return response.json()["access_token"]


@pytest.mark.parametrize(
    "params, expected_status",
    [
        ({}, 200),
        ({"first_name": "John"}, 200),
        ({"sort_by": "invalid_field"}, 400),
    ],
)
async def test_get_users(client, db_session, params, expected_status):
    response = await client.get("/api/v1/users/", params=params)
    assert response.status_code == expected_status

    if expected_status == 200:
        assert isinstance(response.json(), list)
        if "first_name" in params:
            assert all(
                user["first_name"] == params["first_name"]
                for user in response.json()
            )
        elif "sort_by" in params and params["sort_by"] == "invalid_field":
            res = "Invalid sort_by field: invalid_field"
            assert response.json()["detail"] == res
