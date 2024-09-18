import typing as t
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import Boolean, DateTime, Index, Integer, String, event
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

Role = t.Literal["user", "admin"]


class User(Base):
    """
    Model representing a user
    """

    first_name: Mapped[str] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str] = mapped_column(String(50), nullable=True)
    email: Mapped[str] = mapped_column(String, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[Role] = mapped_column(
        String, index=True, nullable=False, default="user"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now(timezone.utc),
    )
    balance: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    block_status: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    block_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    __table_args__ = (
        Index("user_email", "email"),
        Index("user_last_activity_at", "last_activity_at"),
        Index("user_block_status", "block_status"),
        Index("user_balance", "balance"),
    )

    def __repr__(self) -> str:
        """
        Provides a string representation of the User object, showing the email.
        """
        return f"User(email={self.email})"

    def as_dict(self):
        """
        Converts the User object to a dictionary representation,
        including email, password, and role.
        """
        return {
            "email": self.email,
            "password": self.password,
            "role": self.role,
        }

    @staticmethod
    def update_timestamp(mapper, connection, target):
        """
        Updates the updated_at timestamp before the User object
        is updated in the database.
        """
        target.updated_at = datetime.now(timezone.utc)

    @staticmethod
    def check_admin_balance(user):
        """
        Ensure admins cannot have an active balance.
        """
        if user.role == "admin" and user.balance > 0:
            raise HTTPException(
                status_code=400, detail="Admins cannot have an active balance"
            )

    @staticmethod
    def before_insert_or_update(mapper, connection, target):
        """
        Validates before inserting or updating a User object.
        Ensures that an admin cannot have an active balance.
        """
        User.check_admin_balance(target)


event.listen(User, "before_update", User.before_insert_or_update)
event.listen(User, "before_insert", User.before_insert_or_update)
event.listen(User, "before_update", User.update_timestamp)
