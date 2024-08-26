import pytest

pytestmark = pytest.mark.anyio


test_register_cases = (
    ("testuser1@example.com", "dSihhd2dy42/S", 201),
    ("testuser1@example.com", "dSihhd2dy42/S", 400),
    ("testuser3@example.com", "dSi243", 422),
)


@pytest.mark.parametrize(
    "email, password, status",
    test_register_cases,
)
async def test_register_user(
    client, db_session, email, password, status
) -> None:
    response = await client.post(
        "/auth/register/",
        json={"email": email, "password": password},
    )
    assert response.status_code == status


# test_login_cases = (
#     ("testuser1@example.com", "dSWRONGihhd2dy42/S", 401),
#     ("testuser1@example.com", "dSihhd2dy42/S", 200),
#     ("testuser3@example.com", "dSi243", 401),
# )
#
#
# @pytest.mark.parametrize(
#     "email, password, status",
#     test_login_cases,
# )
# async def test_login_user(client, db_session, email, password, status)->None:
#     response = await client.post(
#         "/auth/login/",
#         json={"email": email, "password": password},
#     )
#     assert response.status_code == status


# test_logout_cases = (
#     ("valid_access_token", 200),
#     ("blacklisted_token", 401),
#     ("invalid_token", 401),
# )
#
#
# @pytest.mark.parametrize(
#     "token, status",
#     test_logout_cases,
# )
# async def test_logout_user(client, db_session, token, status) -> None:
#     response = await client.post(
#         "/auth/logout/",
#         headers={"Authorization": f"Bearer {token}"},
#     )
#     assert response.status_code == status
#
#
# test_change_password_cases = (
#     ("testuser1@example.com", "dSihhd2dy42/S", "newpassword1/S", 200),
#     ("testuser1@example.com", "wrongpassword", "newpassword1/S", 401),
#     ("nonexistent@example.com", "somepassword", "newpassword1/S", 401),
# )
#
#
# @pytest.mark.parametrize(
#     "email, current_password, new_password, status",
#     test_change_password_cases,
# )
# async def test_change_password(
#     client, db_session, email, current_password, new_password, status
# ) -> None:
#     response = await client.post(
#         "/auth/change_password/",
#         data={
#             "current_password": current_password,
#             "new_password": new_password,
#         },
#         headers={"Authorization": f"Bearer {email}"},
#     )
#     assert response.status_code == status
#
#
# test_refresh_cases = (
#     ("valid_refresh_token", 200),
#     ("blacklisted_token", 401),
#     ("invalid_token", 401),
# )
#
#
# @pytest.mark.parametrize(
#     "token, status",
#     test_refresh_cases,
# )
# async def test_refresh_token(client, db_session, token, status) -> None:
#     response = await client.post(
#         "/auth/refresh/",
#         headers={"Authorization": f"Bearer {token}"},
#     )
#     assert response.status_code == status
