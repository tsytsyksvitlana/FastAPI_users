from fastapi import Depends, HTTPException, status

from web_app.api.v1.routers.auth.router import get_current_user


def admin_permission(user=Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You do not have permission to perform this action",
        )
    return user


def user_permission(user=Depends(get_current_user)):
    if user.role != "user":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You do not have permission to perform this action",
        )
