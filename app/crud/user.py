import logging
from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import timedelta

from app.models import User as DBModelUser
from app.schemas.auth import Signup
from app.schemas.user import UpdateProfile, ResetPasswordArgs
from app.utils.auth import hash_password, utc_now, is_protected_username, verify_password
from app.services.auth import new_token


logging.basicConfig(level=logging.DEBUG)


async def get_all_users(db_session: AsyncSession) -> List[DBModelUser]:

    stmt = select(DBModelUser)
    result = await db_session.execute(stmt)
    users = result.scalars().all()

    return users


async def get_user(db_session: AsyncSession, user_id: UUID):
    return await db_session.scalar(
        select(DBModelUser).filter(DBModelUser.id == user_id)
    )



async def get_user_by_username(db_session: AsyncSession, username: str) -> DBModelUser | None:
    return await db_session.scalar(
        select(DBModelUser).filter(func.lower(DBModelUser.username) == username.lower())
    )

async def get_user_by_email(db_session: AsyncSession, email: str) -> DBModelUser | None:
    return await db_session.scalar(
        select(DBModelUser).filter(func.lower(DBModelUser.email) == email.lower())
    )



async def get_admin_user_by_email(db_session: AsyncSession, email: str) -> DBModelUser | None:
    return await db_session.scalar(
        select(DBModelUser).filter(
            func.lower(DBModelUser.email) == email.lower(),
            DBModelUser.role == "admin"
        )
    )


async def create_user(db_session: AsyncSession, signup: Signup) -> DBModelUser:
    password_hash = hash_password(signup.password)
    now = utc_now()

    user = DBModelUser(
        username=signup.username,
        email=signup.email,
        hashed_password=password_hash,
        created=now,
    )

    db_session.add(user)
    await db_session.commit()

    return user


async def update_user_profile(db_session: AsyncSession, current_user: DBModelUser, profile_update: UpdateProfile):
    if profile_update.username:
        if is_protected_username(profile_update.username):
            logging.debug(f"Invalid username detected: {profile_update.username}")
            raise HTTPException(status_code=400, detail="Invalid username")

        if await get_user_by_username(db_session, profile_update.username):
            logging.debug(f"Username already exists: {profile_update.username}")
            raise HTTPException(status_code=400, detail="Username already exists")

        current_user.username = profile_update.username

    if profile_update.email:
        if await get_user_by_email(db_session, profile_update.email):
            logging.debug(f"Email already    exists: {profile_update.email}")
            raise HTTPException(status_code=400, detail="Email already exists")

        current_user.email = profile_update.email

    await db_session.commit()

    return current_user


async def create_password_token(db_session: AsyncSession, user: DBModelUser):
    user.password_reset_expire = utc_now() + timedelta(hours=1)
    user.password_reset_token = new_token()

    db_session.add(user)
    await db_session.commit()

    return user


async def create_new_password(db_session: AsyncSession, user: DBModelUser, reset_password_args: ResetPasswordArgs):
    # Проверка, что текущий пароль верный
    if not verify_password(reset_password_args.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")

    # Установка нового хэша пароля
    user.hashed_password = hash_password(reset_password_args.password)
    user.password_reset_expire = None
    user.password_reset_token = None

    db_session.add(user)
    await db_session.commit()
