from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from web_app.api.v1.routers.auth.router import get_current_user
from web_app.db.db_helper import db_helper
from web_app.models.user import User
from web_app.schemas.user import (
    BalanceUpdateS,
    UserFilterS,
    UserProfileS,
    UserResponseS,
    UserUpdateS,
)

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.post("/", response_model=List[UserResponseS])
async def get_users(
    filters: UserFilterS,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    order_func = asc if filters.sort_order == "asc" else desc

    query = select(User)

    if filters.id is not None:
        query = query.where(User.id == filters.id)
    if filters.first_name is not None:
        query = query.where(User.first_name == filters.first_name)
    if filters.last_name is not None:
        query = query.where(User.last_name == filters.last_name)
    if filters.block_status is not None:
        query = query.where(User.block_status == filters.block_status)

    sort_field = getattr(User, filters.sort_by)
    query = query.order_by(order_func(sort_field))

    result = await session.execute(query)
    users = result.scalars().all()

    return users


@router.get("/profile/", response_model=List[UserProfileS])
async def retrieve_profiles(
    session: AsyncSession = Depends(db_helper.session_getter),
):
    query = select(User).where(
        User.first_name.isnot(None), User.last_name.isnot(None)
    )
    result = await session.execute(query)
    profiles = result.scalars().all()

    return profiles


@router.get("/profile/me/", response_model=UserProfileS)
async def retrieve_profile(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    query = select(User).where(
        User.email == user.email,
        User.first_name.isnot(None),
        User.last_name.isnot(None),
    )
    result = await session.execute(query)
    user_profile = result.scalars().first()

    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
        )

    return user_profile


@router.put("/profile/", response_model=UserUpdateS)
async def update_profile(
    update_data: UserUpdateS,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    query = select(User).where(User.email == user.email)
    result = await session.execute(query)
    user_profile = result.scalars().first()

    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    updated_fields = update_data.model_dump(exclude_unset=True)

    for field, value in updated_fields.items():
        setattr(user_profile, field, value)

    session.add(user_profile)
    await session.commit()

    return user_profile


@router.get("/{id}/balance/", response_model=int)
async def get_balance(
    id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    query = select(User.balance).where(User.id == id)
    result = await session.execute(query)
    balance = result.scalar()

    if balance is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return balance


@router.put("/{id}/balance/", response_model=UserResponseS)
async def update_balance(
    id: int,
    update_data: BalanceUpdateS,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    query = select(User).where(User.id == id)
    result = await session.execute(query)
    user_profile = result.scalars().first()

    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user_profile.balance = update_data.balance

    session.add(user_profile)
    await session.commit()

    return user_profile
