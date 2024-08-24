import pytest
from fastapi import status

pytestmark = pytest.mark.anyio


async def test_register_user(client, db_session):
    response = await client.post(
        "/auth/register/",
        json={"email": "testuser@example.com", "password": "dSihhd2dy42/S"},
    )
    assert response.json() == {"msg": "User successfully registered"}
    assert response.status_code == status.HTTP_201_CREATED
