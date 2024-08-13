from fastapi import APIRouter, Depends, Form, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from web_app.auth import utils
from web_app.db.db_helper import db_helper
from web_app.models.user import User
from web_app.schemas.user import UserS

router = APIRouter(prefix="/auth", tags=["auth"])


class Token(BaseModel):
    access_token: str
    token_type: str


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
    payload = {
        "email": user.email,
    }
    token = utils.encode_jwt(payload)
    return Token(access_token=token, token_type="Bearer")
