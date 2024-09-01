import re
from datetime import datetime
from typing import ClassVar, Optional

from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator


class UserS(BaseModel):
    email: EmailStr
    password: str

    PASSWORD_REGEX: ClassVar[re.Pattern] = re.compile(
        r"^"
        r"(?=.*[a-zA-Zа-яА-Я])"
        r"(?=.*[a-zа-я])"
        r"(?=.*[A-ZА-Я])"
        r"(?=.*\d)"
        r"(?=.*[^\w\s@\"'<>\-])"
        r".{8,24}$"
    )

    @field_validator("password")
    def validate_password(cls, v):
        if not cls.PASSWORD_REGEX.match(v):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Password must be 8-24 characters long, contain digits, "
                "lowercase and uppercase letters of any alphabet, "
                "and special characters except for @, \", ', <, >.",
            )
        return v


class UserResponseSchema(BaseModel):
    id: int
    first_name: Optional[str]
    last_name: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    last_activity_at: datetime
    balance: int

    class Config:
        orm_mode = True
