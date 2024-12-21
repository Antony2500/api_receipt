from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Enum, Numeric
from datetime import datetime

from .base import Base


class User(Base):
    __tablename__ = "service_users"

    username: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    email: Mapped[str] = mapped_column(String(255), index=True, unique=True)
    hashed_password: Mapped[str] = mapped_column(nullable=True)
    created: Mapped[datetime]

    email_confirmed: Mapped[bool] = mapped_column(default=False)
    banned: Mapped[bool] = mapped_column(default=False)

    role: Mapped[str] = mapped_column(Enum("user", "admin", name="user_roles"), default="user")

    password_reset_token: Mapped[str] = mapped_column(String(64), nullable=True)
    password_reset_expire: Mapped[datetime] = mapped_column(nullable=True)


    refresh_tokens: Mapped[list["AuthToken"]] = relationship("AuthToken", back_populates="user", cascade="all, delete-orphan")
    sales_receipts: Mapped[list["SalesReceipt"]] = relationship("SalesReceipt", back_populates="user")