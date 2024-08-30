from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):
    email: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    password: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self) -> str:
        return f"User(email={self.email})"

    def as_dict(self):
        return {
            "email": self.email,
            "password": self.password,
        }