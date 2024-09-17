from fastapi import Depends, HTTPException, status

from web_app.api.v1.routers.auth.router import get_current_user
from web_app.models import User


async def check_permission(
    required_role: str,
    user: User = Depends(get_current_user),
):
    if user.role != required_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )
    return user


async def admin_permission(user: User = Depends(get_current_user)):
    return await check_permission("admin", user)


async def user_permission(user: User = Depends(get_current_user)):
    return await check_permission("user", user)
