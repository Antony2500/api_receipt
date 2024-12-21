from . import BaseModel, datetime_pd, UsernameArgs, PasswordArgs, EmailArgs
from app.models.user import User

from pydantic import Field


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None


class TokenData(BaseModel):
    email: str


class TokenResponse(BaseModel):
    expiration: datetime_pd = Field(examples=[1686088809])
    created: datetime_pd = Field(examples=[1686088809])
    secret: str = Field(
        examples=["CQE-CTXVFCYoUpxz_6VKrHhzHaUZv68XvxV-3AvQbnA"]
    )


class Signup(UsernameArgs, PasswordArgs, EmailArgs):
    pass


class LoginArgs(PasswordArgs, EmailArgs):
    pass


class LoginValidationResult(BaseModel):
    user: User
    refresh_token_id: str | None = None

    class Config:
        arbitrary_types_allowed = True

