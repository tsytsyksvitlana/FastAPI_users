import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import asc, desc
from sqlalchemy.exc import SQLAlchemyError
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
from web_app.services.auth.permissions import admin_permission, user_permission

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.post("/", response_model=List[UserResponseS])
async def get_users(
    filters: UserFilterS,
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(admin_permission),
):
    order_func = asc if filters.sort_order == "asc" else desc

    query = select(User).where(User.is_deleted.is_(False))

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
    async with session:
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

        try:
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while updating the profile",
            ) from e

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

    await session.merge(user_profile)
    await session.commit()

    return user_profile


@router.delete("/{id}/delete/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    id: int,
    user: User = Depends(user_permission),
    session: AsyncSession = Depends(db_helper.session_getter),
) -> None:
    """
    Marks the user's account as deleted.
    """
    if user.id != id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )

    query = select(User).where(User.id == id)
    result = await session.execute(query)
    user_obj = result.scalars().first()

    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if user_obj.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is already deleted",
        )

    user_obj.is_deleted = True

    session.add(user_obj)
    await session.commit()


@router.get(
    "/deleted/",
    response_model=List[UserResponseS],
    status_code=status.HTTP_200_OK,
)
async def get_deleted_users(
    limit: int = Query(default=10, ge=1),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(admin_permission),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    """
    Gets deleted users. Requires admin role.
    """
    query = (
        select(User)
        .where(User.is_deleted.is_(True))
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(query)
    users = result.scalars().all()

    return users


async def change_block_status(
    user_id: int, block_status: bool, session: AsyncSession
):
    """
    Helper function to change block status for a user.
    """
    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    user_to_update = result.scalar_one_or_none()

    if not user_to_update or user_to_update.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user_to_update.block_status = block_status
    await session.commit()

    return user_to_update


@router.patch(
    "/{user_id}/block/",
    response_model=UserResponseS,
    status_code=status.HTTP_200_OK,
)
async def block_user(
    user_id: int,
    user: User = Depends(admin_permission),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    """
    Blocks a user by ID. Requires admin role.
    """
    return await change_block_status(user_id, True, session)


@router.patch(
    "/{user_id}/unblock/",
    response_model=UserResponseS,
    status_code=status.HTTP_200_OK,
)
async def unblock_user(
    user_id: int,
    user: User = Depends(admin_permission),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    """
    Unblocks a user by ID. Requires admin role.
    """
    return await change_block_status(user_id, False, session)
