import pytest

pytestmark = pytest.mark.anyio


@pytest.fixture
async def valid_tokens(client, db_session):
    tokens = []
    login_cases = [
        ("testuser1@example.com", "dSihhd2dy42/S"),
    ]
    for email, password in login_cases:
        response = await client.post(
            "/api/v1/auth/login/", data={"email": email, "password": password}
        )
        if response.status_code == 200:
            tokens.append(response.json())
    return tokens


test_register_cases = (
    ("testuser1@example.com", "dSihhd2dy42/S", 201),
    ("testuser1@example.com", "dSihhd2dy42/S", 400),
    ("testuser3@example.com", "dSi243", 422),
)


@pytest.mark.parametrize("email, password, status", test_register_cases)
async def test_register_user(
    client, db_session, email, password, status
) -> None:
    response = await client.post(
        "/api/v1/auth/register/", json={"email": email, "password": password}
    )
    assert response.status_code == status


test_login_cases = (
    ("testuser1@example.com", "dSWRONGihhd2dy42/S", 401),
    ("testuser1@example.com", "dSihhd2dy42/S", 200),
    ("testuser3@example.com", "dSi243", 401),
)

tokens = []


@pytest.mark.parametrize("email, password, status", test_login_cases)
async def test_login_user(client, db_session, email, password, status) -> None:
    response = await client.post(
        "/api/v1/auth/login/", data={"email": email, "password": password}
    )
    print(f"Login response: {response.json()}")
    assert response.status_code == status
    if response.status_code == 200:
        token = response.json().get("access_token")
        print(f"Access token: {token}")
        tokens.append(response.json())


test_change_password_cases = (
    (0, "dSihhd2dy42/S", "newpassword1/S", 200),
    (0, "newpassword1/S", "dSihhd2dy42/S", 200),
    (0, "wrongpassword", "newpassword1/S", 401),
    (None, "somepassword", "newpassword1/S", 401),
)


@pytest.mark.parametrize(
    "token_index, current_password, new_password, status",
    test_change_password_cases,
)
async def test_change_password(
    client,
    db_session,
    valid_tokens,
    token_index,
    current_password,
    new_password,
    status,
) -> None:
    if token_index is not None and len(tokens) > token_index:
        token = tokens[token_index]["access_token"]
    else:
        token = "invalid_token"

    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = await client.post(
        "/api/v1/auth/change_password/",
        data={
            "current_password": current_password,
            "new_password": new_password,
        },
        headers=headers,
    )
    assert response.status_code == status


test_refresh_cases = (
    (0, 200),
    (None, 401),
)


@pytest.mark.parametrize("token_index, status", test_refresh_cases)
async def test_refresh_token(client, db_session, token_index, status) -> None:
    if token_index is not None and len(tokens) > token_index:
        token = tokens[token_index]["access_token"]
    else:
        token = "invalid_token"

    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = await client.post("/api/v1/auth/refresh/", headers=headers)
    assert response.status_code == status


test_logout_cases = (
    (0, 200),
    (0, 401),
)


@pytest.mark.parametrize("token_index, status", test_logout_cases)
async def test_logout_user(client, db_session, token_index, status) -> None:
    token = tokens[token_index].get("access_token")

    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = await client.post("/api/v1/auth/logout/", headers=headers)
    assert response.status_code == status
