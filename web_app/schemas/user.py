import re
from datetime import datetime
from typing import ClassVar, Optional

from fastapi import HTTPException, status
from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    constr,
    field_validator,
)


class UserCreateS(BaseModel):
    """
    Schema for user creation.
    """

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

    @field_validator("first_name", "last_name", mode="before")
    def validate_names(cls, value, field):
        if value and not re.match(r"^[A-Za-z]+$", value):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field.name} must only contain alphabetic characters.",
            )
        return value


class UserUpdateS(BaseModel):
    """
    Schema for user update.
    """

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    balance: Optional[int] = Field(None, ge=0)

    @field_validator("first_name", "last_name", mode="before")
    def validate_names(cls, value, field):
        if value and value.strip() == "":
            return None
        if value and not re.match(r"^[A-Za-z]+$", value):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field.name} must only contain alphabetic characters.",
            )
        return value


class UserResponseS(BaseModel):
    """
    Schema for response with user's data.
    """

    id: int
    first_name: Optional[str]
    last_name: Optional[str]
    role: str
    created_at: datetime
    updated_at: Optional[datetime]
    last_activity_at: datetime
    block_status: bool
    block_at: Optional[datetime]
    balance: int

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class UserProfileS(BaseModel):
    """
    Schema for user profile.
    """

    first_name: str
    last_name: str
    created_at: datetime
    updated_at: Optional[datetime]
    last_activity_at: datetime
    balance: int

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class BalanceUpdateS(BaseModel):
    """
    Schema for updating user's balance.
    """

    balance: Optional[int] = Field(None, ge=0)


class UserFilterS(BaseModel):
    """
    Schema for filtering and sorting users.
    """

    id: Optional[int] = None
    first_name: Optional[constr(max_length=50)] = Field(None)
    last_name: Optional[constr(max_length=50)] = Field(None)
    block_status: Optional[bool] = None
    sort_by: str = Field("id")
    sort_order: str = Field("asc")

    @field_validator("first_name", "last_name", mode="before")
    def validate_names(cls, value, field):
        if value and not re.match(r"^[A-Za-z]+$", value):
            raise ValueError(
                f"{field.name} must only contain alphabetic characters."
            )
        return value

    @field_validator("sort_by", mode="before")
    def validate_sort_by(cls, value):
        if not re.match(r"^(id|balance|last_activity_at)$", value):
            raise ValueError(
                "Sort by field must be one of: id, balance, last_activity_at."
            )
        return value

    @field_validator("sort_order", mode="before")
    def validate_sort_order(cls, value):
        if not re.match(r"^(asc|desc)$", value):
            raise ValueError("Sort order must be either 'asc' or 'desc'.")
        return value
