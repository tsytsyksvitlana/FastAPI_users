from datetime import datetime, timedelta

import bcrypt
import jwt
from fastapi import HTTPException, status
from jwt.exceptions import DecodeError, ExpiredSignatureError

from .config import auth_jwt


def encode_jwt(
    payload: dict,
    key: str = auth_jwt.private_key_path.read_text(),
    algorithm: str = auth_jwt.algorithm,
    expire_minutes: int = auth_jwt.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None,
):
    to_encode = payload.copy()
    now = datetime.utcnow()
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(
        exp=expire,
        iat=now,
    )
    encoded = jwt.encode(to_encode, key, algorithm=algorithm)
    return encoded


def decode_jwt(token: str | bytes, public_key: str, algorithm: str):
    try:
        decoded = jwt.decode(token, public_key, algorithms=[algorithm])
        return decoded
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    except DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalid"
        )


def hash_password(
    password: str,
) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)


def validate_password(
    password: str,
    hashed_password: bytes,
) -> bool:
    hashed_password_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password_bytes)
