import re
from datetime import datetime
from typing import ClassVar, Optional

from fastapi import HTTPException, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreateS(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
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


class UserUpdateS(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    balance: Optional[int] = Field(None, ge=0)


class UserResponseS(BaseModel):
    id: int
    first_name: Optional[str]
    last_name: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    last_activity_at: datetime
    balance: int

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class UserProfileS(BaseModel):
    first_name: str
    last_name: str
    created_at: datetime
    updated_at: Optional[datetime]
    last_activity_at: datetime
    balance: int

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class BalanceUpdateS(BaseModel):
    balance: int
