import pytest
from fastapi import status

pytestmark = pytest.mark.anyio


test_register_cases = (("testuser@example.com", "dSihhd2dy42/S"),)


@pytest.mark.parametrize(
    "email, password",
    test_register_cases,
)
async def test_register_user(client, db_session, email, password) -> None:
    response = await client.post(
        "/auth/register/",
        json={"email": email, "password": password},
    )
    assert response.json() == {"detail": "User successfully registered"}
    assert response.status_code == status.HTTP_201_CREATED
