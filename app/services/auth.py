import os
import uuid

import jwt
import secrets
from fastapi import Depends, HTTPException, Request
from datetime import datetime, timezone, timedelta
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.errors import credentials_exception
from app.models import AuthToken
from app.schemas.user import User
from app.constants import TOKEN_TYPE_FIELD, ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE
from app.models.user import User as DB_User
from app.utils.auth import utc_now

ACCESS_TOKEN_SECRET_KEY = settings.auth_jwt.access_token_secret_key
ACCESS_TOKEN_ALGORITHM = settings.auth_jwt.access_token_algorithm


def new_token():
    """
        Generate new random token

    :returns: The new random token
    """
    return secrets.token_urlsafe(32)


def get_access_token(request: Request):
    token = request.session.get('access_token')

    if not bool(token):
        raise HTTPException(status_code=401, detail="Invalid access token")

    return token


def get_email_from_token_payload(token: str | bytes) -> str:
    payload = decode_jwt(token)
    if payload.get("type") != ACCESS_TOKEN_TYPE:
        raise credentials_exception

    email = payload.get("sub")
    if email is None:
        raise credentials_exception

    return email


def decode_jwt(
        token: str | bytes,
        public_key: str = settings.auth_jwt.public_key_path.read_text(),
        algorithm: str = ACCESS_TOKEN_ALGORITHM,
        verify_exp: bool = True
) -> dict:
    decoded = jwt.decode(
        token,
        public_key,
        algorithms=[algorithm],
        options={"verify_exp": verify_exp}
    )
    return decoded


def encode_jwt(
        payload: dict,
        private_key: str = settings.auth_jwt.private_key_path.read_text(),
        algorithm: str = ACCESS_TOKEN_ALGORITHM,
        expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
        expire_timedelta: timedelta | None = None
) -> str:
    to_encode = payload.copy()
    now = datetime.utcnow()

    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)

    to_encode.update(
        exp=expire,
        iat=now,
        jti=str(uuid.uuid4()),
    )
    encoded = jwt.encode(
        to_encode,
        private_key,
        algorithm=algorithm
    )
    return encoded


def get_token_payload(
        token: str,
        check_expired_token: bool = True
) -> dict:
    try:
        payload = decode_jwt(token=token, verify_exp=check_expired_token)
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token error: {e}"
        )
    return payload


def validate_token_type(
        payload: dict,
        token_type: str,
) -> bool:
    current_token_type = payload.get(TOKEN_TYPE_FIELD)
    if current_token_type == token_type:
        return True
    raise HTTPException(
        status_code=401,
        detail=f"Invalid token type {current_token_type!r} expected {token_type!r}"
    )


def check_auth_user_from_token_by_payload(
    token_type: str,
    user_email: str,
    payload: dict,
) -> bool:
    try:
        validate_token_type(payload, token_type)
        if payload.get("sub") != user_email:
            return False
        return True
    except Exception as e:
        return False


def create_jwt(
        token_type: str,
        token_data: dict,
        expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
        expire_timedelta: timedelta | None = None,
) -> str:
    jwt_payload = {TOKEN_TYPE_FIELD: token_type}
    jwt_payload.update(token_data)
    return encode_jwt(
        payload=jwt_payload,
        expire_minutes=expire_minutes,
        expire_timedelta=expire_timedelta,
    )


def create_access_token(user: User, refresh_token: AuthToken) -> str:
    jwt_payload = {
        "sub": user.email,
        "refresh_token_id": str(refresh_token.id)
    }
    return create_jwt(
        token_type=ACCESS_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_minutes=settings.auth_jwt.access_token_expire_minutes,
    )


def create_refresh_token(user: User) -> str:
    jwt_payload = {
        "sub": user.email,
    }
    return create_jwt(
        token_type=REFRESH_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_timedelta=timedelta(days=settings.auth_jwt.refresh_token_expire_days),
    )
