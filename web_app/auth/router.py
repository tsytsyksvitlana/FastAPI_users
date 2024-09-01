import json
import logging

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.security import HTTPBearer
from redis.asyncio import Redis
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from web_app.auth import utils
from web_app.auth.config import (
    BLOCK_TIME_SECONDS,
    MAX_ATTEMPTS,
    PUBLIC_KEY,
    auth_jwt,
)
from web_app.auth.jwt_helper import (
    Token,
    create_access_token,
    create_refresh_token,
)
from web_app.db.db_helper import db_helper
from web_app.models.user import User
from web_app.schemas.user import UserCreateS

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

http_bearer = HTTPBearer(auto_error=True)

redis = Redis.from_url(
    "redis://redis:6379/0", encoding="utf-8", decode_responses=True
)

logger = logging.getLogger(__name__)


def get_redis_client() -> Redis:
    return redis


async def get_user_from_redis(email: str) -> User | None:
    """
    Gets user from Redis based on email.
    Returns None if no user is found.
    """
    user_data = await redis.get(email)
    if user_data:
        user_dict = json.loads(user_data)
        return User(**user_dict)


async def set_user_to_redis(email: str, user: User) -> None:
    """
    Saves user to Redis.
    """
    user_dict = user.as_dict()
    await redis.set(email, json.dumps(user_dict), ex=300)


async def check_block(ip: str, redis: Redis) -> bool:
    """
    Returns is ip blocked or not.
    """
    block_key = f"block:{ip}"
    blocked = await redis.get(block_key)
    return blocked is not None


async def increment_attempts(ip: str, redis: Redis):
    """
    Increments number of attempts.
    If amount of retries exceeds MAX_ATTEMPTS, ip blocks
    for BLOCK_TIME_SECONDS and counter is set to 0.
    """
    attempts_key = f"attempts:{ip}"
    block_key = f"block:{ip}"

    attempts = await redis.incr(attempts_key)
    if attempts == 1:
        await redis.expire(attempts_key, BLOCK_TIME_SECONDS)

    if attempts >= MAX_ATTEMPTS:
        await redis.set(block_key, "blocked", ex=BLOCK_TIME_SECONDS)
        await redis.delete(attempts_key)


async def get_client_ip(request: Request) -> str:
    """
    Gets the client's IP address from the request headers.
    """
    ip = request.client.host
    return ip


async def validate_auth_user(
    email: str = Form(),
    password: str = Form(),
    ip: str = Depends(get_client_ip),
    redis: Redis = Depends(get_redis_client),
    session: AsyncSession = Depends(db_helper.session_getter),
) -> User:
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
    )

    if await check_block(ip, redis):
        logger.warning(
            f"IP {ip} is blocked due to too many failed login attempts."
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Too many failed login attempts. Try again later.",
        )

    user = await get_user_from_redis(email)
    if not user:
        query = select(User).where(User.email == email)
        result = await session.execute(query)
        user = result.scalars().first()
        if user:
            await set_user_to_redis(email, user)
        else:
            logger.warning(f"Login failed for email: {email}. User not found.")
            await increment_attempts(ip, redis)
            raise unauthed_exc

    if not utils.validate_password(
        password=password,
        hashed_password=user.password,
    ):
        logger.warning(f"Login failed for email: {email}. Incorrect password.")
        await increment_attempts(ip, redis)
        raise unauthed_exc

    return user


@router.post("/register/", status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserCreateS, session: AsyncSession = Depends(db_helper.session_getter)
) -> dict[str, str]:
    """
    Registers a new user.
    Raises HTTP 400 if user already exists.
    """
    query = select(User).where(User.email == user.email)
    result = await session.execute(query)
    existing_user = result.scalars().first()

    if existing_user:
        logger.warning(
            f"Registration failed. User with email {user.email} already exists."
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    hashed_password = utils.hash_password(user.password).decode("utf-8")
    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password=hashed_password,
    )
    session.add(new_user)
    await session.commit()

    return {"detail": "User successfully registered"}


@router.post("/login/", response_model=Token)
async def login(user: User = Depends(validate_auth_user)) -> Token:
    """
    Function logs in a user and returns an access token and a refresh token.
    """
    access_token = create_access_token(user.email)
    refresh_token = create_refresh_token(user.email)
    return Token(access_token=access_token, refresh_token=refresh_token)


async def add_token_to_blacklist(token: str) -> None:
    """
    Saves token to blacklist and adds it to redis.
    """
    await redis.set(
        token, "blacklisted", ex=auth_jwt.access_token_expire_minutes * 60
    )


async def is_token_blacklisted(token: str) -> bool:
    return await redis.exists(token)


@router.post("/logout/", status_code=status.HTTP_200_OK)
async def logout(
    token: str = Depends(http_bearer),
    session: AsyncSession = Depends(db_helper.session_getter),
) -> dict[str, str]:
    """
    Logs out a user.
    """
    token = token.credentials
    if await is_token_blacklisted(token):
        logger.warning(
            f"Logout attempt with already blacklisted token: {token}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is already blacklisted",
        )

    await add_token_to_blacklist(token)
    return {"msg": "Logged out successfully"}


@router.post(
    "/refresh/", response_model=Token, response_model_exclude_none=True
)
async def auth_refresh_jwt(token: str = Depends(http_bearer)) -> Token:
    """
    Refreshes a JWT token.
    Returns new tokens for valid access or refresh tokens.
    Returns HTTP 401 for invalid or expired tokens.
    """
    try:
        token = token.credentials
        algorithm = auth_jwt.algorithm
        payload = utils.decode_jwt(token, PUBLIC_KEY, algorithm)

        token_type = payload.get("type")
        user_email = payload.get("email")

        if not user_email or token_type not in ("access", "refresh"):
            logger.warning("Token refresh failed due to invalid payload.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        if token_type == "access":
            new_refresh_token = create_refresh_token(user_email)
            return Token(access_token=token, refresh_token=new_refresh_token)

        elif token_type == "refresh":
            new_access_token = create_access_token(user_email)
            return Token(access_token=new_access_token, refresh_token=token)

    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


async def get_current_user(
    token: str = Depends(http_bearer),
    session: AsyncSession = Depends(db_helper.session_getter),
    redis: Redis = Depends(get_redis_client),
) -> User:
    """
    Gets the current user based on the JWT token.
    Checks if the token is blacklisted and validates it.
    Retrieves and returns the user from the cache or database.
    Raises HTTP 401 if the token is blacklisted, invalid, or user not found.
    """
    token = token.credentials
    if await is_token_blacklisted(token):
        logger.warning(f"Token is blacklisted: {token}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is blacklisted",
        )

    algorithm = auth_jwt.algorithm
    payload = utils.decode_jwt(token, PUBLIC_KEY, algorithm)

    user_email = payload.get("email")
    if not user_email:
        logger.warning("Token validation failed. Invalid token.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    cached_user = await get_user_from_redis(user_email)
    if cached_user:
        return cached_user

    query = select(User).where(User.email == user_email)
    result = await session.execute(query)
    user = result.scalars().first()
    if not user:
        logger.warning(f"User not found for email: {user_email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    await set_user_to_redis(user_email, user)

    return user


@router.post("/change_password/", status_code=status.HTTP_200_OK)
async def change_password(
    current_password: str = Form(),
    new_password: str = Form(),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(db_helper.session_getter),
) -> dict[str, str]:
    """
    Changes the password.
    Raises HTTP 401 for invalid or expired tokens.
    """
    if not utils.validate_password(
        password=current_password, hashed_password=user.password
    ):
        logger.warning(
            f"Password change failed for user: {user.email}."
            f" Incorrect current password."
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect current password",
        )

    hashed_new_password = utils.hash_password(new_password).decode("utf-8")
    try:
        user.password = hashed_new_password
        await session.flush()
        await session.commit()
    except IntegrityError:
        logger.error("IntegrityError occurred while changing password.")
        await session.rollback()

        query = select(User).where(User.email == user.email)
        result = await session.execute(query)
        user = result.scalars().first()

        if not user:
            logger.error(
                f"User with email {user.email} not found after rollback."
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        user.password = hashed_new_password
        session.add(user)
        await session.commit()

    await set_user_to_redis(user.email, user)

    return {"msg": "Password successfully changed"}
