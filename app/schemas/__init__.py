from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, field_validator, PlainSerializer
from typing import Annotated

from app.utils.auth import to_timestamp

datetime_pd = Annotated[
    datetime,
    PlainSerializer(lambda x: to_timestamp(x),
                    return_type=int,
                    ),
]


class UsernameArgs(BaseModel):
    username: str = Field(pattern="^[A-Za-z][A-Za-z0-9_]{4,63}$", examples=["Antony"])


class NameArgs(BaseModel):
    name: str = Field(pattern="^[A-Za-z][A-Za-z0-9_]{4,63}$", examples=["Crew"])


class EmailArgs(BaseModel):
    email: EmailStr = Field(examples=["your_email@gmail.com"])

    @field_validator("email")
    @classmethod
    def check_email(cls, value: EmailStr) -> EmailStr:
        if "+" in value:
            raise ValueError("Email contains unacceptable characters")
        
        return value
    

class PasswordArgs(BaseModel):
    password: str = Field(min_length=8, max_length=128, examples=["password"])
