import pytest
from fastapi import status
from sqlalchemy.future import select

from web_app.models.user import User


@pytest.mark.anyio
async def test_health_check(client):
    response = await client.get("/auth/login/")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.anyio
async def test_register_user(client, db_session):
    response = await client.post(
        "/auth/register/",
        json={"email": "testuser@example.com", "password": "dSihhd2dy42/S"},
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"msg": "User successfully registered"}

    query = await db_session.execute(
        select(User).where(User.email == "testuser@example.com")
    )
    user = query.scalar_one_or_none()
    assert user is not None
