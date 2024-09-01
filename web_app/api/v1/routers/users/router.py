from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from web_app.db.db_helper import db_helper
from web_app.models.user import User
from web_app.schemas.user import UserResponseSchema

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/", response_model=List[UserResponseSchema])
async def get_users(
    id: Optional[int] = Query(None),
    first_name: Optional[str] = Query(None),
    last_name: Optional[str] = Query(None),
    block_status: Optional[bool] = Query(None),
    sort_by: str = Query("id"),
    sort_order: str = Query("asc"),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    valid_sort_fields = ["id", "balance", "last_activity_at"]
    valid_sort_orders = ["asc", "desc"]

    if sort_by not in valid_sort_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sort_by field: {sort_by}",
        )

    if sort_order not in valid_sort_orders:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sort_order field: {sort_order}",
        )

    order_func = asc if sort_order == "asc" else desc

    query = select(User)

    if id is not None:
        query = query.where(User.id == id)
    if first_name is not None:
        query = query.where(User.first_name == first_name)
    if last_name is not None:
        query = query.where(User.last_name == last_name)
    if block_status is not None:
        query = query.where(User.block_status == block_status)

    sort_field = getattr(User, sort_by)
    query = query.order_by(order_func(sort_field))

    result = await session.execute(query)
    users = result.scalars().all()

    return users
