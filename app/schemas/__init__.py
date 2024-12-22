from datetime import datetime
from decimal import Decimal

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


class Title(BaseModel):
    title: str = Field(min_length=1, max_length=255, examples=["FPW Dron 6s"])


class Price(BaseModel):
    price: Decimal = Field(gt=0, decimal_places=2)


class Total(BaseModel):
    total: Decimal = Field(gt=0, decimal_places=2)


