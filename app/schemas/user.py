from pydantic import BaseModel, ConfigDict, EmailStr, Field, constr, field_validator
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal

from . import UsernameArgs, PasswordArgs, EmailArgs
from app.models import User as DB_User

class User(PasswordArgs, EmailArgs):
    pass


class AuthorizedUser(UsernameArgs, EmailArgs):
    created: datetime


class AuthorizedUserWithBalance(UsernameArgs, EmailArgs):
    created: datetime
    balance: Decimal = Field(..., max_digits=10, decimal_places=2)

    class Config:
        # Настройки Pydantic для поддержки Decimal
        json_encoders = {Decimal: lambda v: str(v)}

class UpdateProfile(UsernameArgs, EmailArgs):
    username: Optional[constr(pattern="^[A-Za-z][A-Za-z0-9_]{4,63}$")] = Field(
        None,
        examples=["New Username or None"]
    )

    email: Optional[EmailStr] = Field(None, examples=["New Email or None"])

    @field_validator("email")
    @classmethod
    def check_email(cls, value: EmailStr) -> EmailStr:
        if value is None:
            return value
        if "+" in value:
            raise ValueError("Email contains unacceptable characters")

        return value


class ResetPasswordArgs(PasswordArgs):
    old_password: str = Field(min_length=8, max_length=128, examples=["old_password"])


class UserDeleteResponse(BaseModel):
    success: bool


class CurrentUserDataWithRefreshTokenID(BaseModel):
    user: DB_User
    refresh_token_id: Optional[str]

    class Config:
        arbitrary_types_allowed = True