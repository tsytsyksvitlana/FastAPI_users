from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from web_app.auth import utils
from web_app.auth.config import auth_jwt
from web_app.auth.jwt_helper import (
    Token,
    create_access_token,
    create_refresh_token,
)
from web_app.db.db_helper import db_helper
from web_app.models.user import User
from web_app.schemas.user import UserS

router = APIRouter(prefix="/auth", tags=["auth"])

http_bearer = HTTPBearer(auto_error=True)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def validate_auth_user(
    email: str = Form(),
    password: str = Form(),
    session: AsyncSession = Depends(db_helper.session_getter),
) -> User:
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
    )

    query = select(User).where(User.email == email)
    result = await session.execute(query)
    user = result.scalars().first()

    if not user:
        raise unauthed_exc

    if not utils.validate_password(
        password=password,
        hashed_password=user.password,
    ):
        raise unauthed_exc

    return user


@router.post("/register/", status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserS, session: AsyncSession = Depends(db_helper.session_getter)
):
    query = select(User).where(User.email == user.email)
    result = await session.execute(query)
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    hashed_password = utils.hash_password(user.password).decode("utf-8")
    new_user = User(email=user.email, password=hashed_password)
    session.add(new_user)
    await session.commit()

    return {"msg": "User successfully registered"}


@router.post("/login/", response_model=Token)
async def login(user: User = Depends(validate_auth_user)):
    access_token = create_access_token(user.email)
    refresh_token = create_refresh_token(user.email)
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout/", status_code=status.HTTP_200_OK)
async def logout(token: str = Depends(oauth2_scheme)):
    # TODO: make token invalid
    return {"msg": "Logged out successfully"}


@router.post(
    "/refresh/", response_model=Token, response_model_exclude_none=True
)
async def auth_refresh_jwt(token: str = Depends(http_bearer)):
    try:
        token = token.credentials
        public_key = auth_jwt.public_key_path.read_text()
        algorithm = auth_jwt.algorithm
        payload = utils.decode_jwt(token, public_key, algorithm)

        token_type = payload.get("type")
        user_email = payload.get("email")

        if not user_email or token_type not in ("access", "refresh"):
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

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
