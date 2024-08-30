from datetime import timedelta

from pydantic import BaseModel

from web_app.auth import utils
from web_app.auth.config import auth_jwt


class Token(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


def create_jwt(
    token_type: str,
    token_data: dict,
    expire_minutes: int = auth_jwt.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None,
) -> str:
    jwt_payload = {"type": token_type, **token_data}
    return utils.encode_jwt(
        payload=jwt_payload,
        expire_timedelta=expire_timedelta,
        expire_minutes=expire_minutes,
    )


def create_access_token(email: str) -> str:
    payload = {
        "sub": email,
        "email": email,
    }
    return create_jwt(
        token_type="access",
        token_data=payload,
        expire_minutes=auth_jwt.access_token_expire_minutes,
    )


def create_refresh_token(email: str) -> str:
    payload = {
        "email": email,
    }
    return create_jwt(
        token_type="refresh",
        token_data=payload,
        expire_timedelta=timedelta(days=auth_jwt.refresh_token_expire_days),
    )
