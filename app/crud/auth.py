from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
from typing import Optional

from app.models import User as DBModelUser
from app.models import AuthToken
from app.services.auth import create_refresh_token
from app.utils.auth import utc_now
from app.errors import TokenInvalidError


async def create_refresh_auth_token(db_session: AsyncSession, user: DBModelUser) -> AuthToken:
    """
    Create a new refresh auth token for current user

    :param db_session: Asynchronous database session.
    :param user: The user to whom the token is assigned.


    :return: Refresh auth token
    """
    now = utc_now()
    secret = create_refresh_token(user)
    expiration_time = now + timedelta(days=15)


    token = AuthToken(
        **{
            "secret": secret,
            "expiration": expiration_time,
            "created": now,
            "user": user,
            "token_type": "refresh",
        }
    )

    db_session.add(token)
    await db_session.commit()

    return token


async def get_refresh_auth_token(db_session: AsyncSession, user: DBModelUser, token_id: str) -> AuthToken:
    """
    Get the refresh auth token by its ID and check if it belongs to the user.

    :param db_session: Asynchronous database session.
    :param token_id: Token ID.
    :param user: The user to whom the token is assigned.

    :return: Found token or None.
    """
    query = select(AuthToken).where(
        AuthToken.id == token_id,
        AuthToken.user_id == user.id,
        AuthToken.token_type == "refresh"
    )
    result = await db_session.execute(query)
    token = result.scalar_one_or_none()
    return token


async def get_refresh_auth_token_without_user(db_session: AsyncSession, token_id: str) -> AuthToken:
    """
    Get the refresh auth token by its ID without checking the user.

    :param db_session: Asynchronous database session.
    :param token_id: Token ID.

    :return: Found token or None.
    """
    query = select(AuthToken).where(
        AuthToken.id == token_id,
        AuthToken.token_type == "refresh"
    )
    result = await db_session.execute(query)
    token = result.scalar_one_or_none()
    return token


async def update_refresh_auth_token(db_session: AsyncSession, user: DBModelUser, token_id: str) -> AuthToken:
    """
        Update an existing refresh auth token by its ID.

        :param db_session: Asynchronous database session.
        :param user: The user who owns the token.
        :param token_id: ID of the token to be updated.

        :return: Updated AuthToken object.
        :raises HTTPException: If the token is not found or does not belong to the user.
    """

    token = await get_refresh_auth_token(db_session, user, token_id)

    if not token:
        raise TokenInvalidError(f"Token with ID {token_id} not found or does not belong to user {user.id}")

    now = utc_now()
    token.secret = create_refresh_token(user)
    token.expiration = now + timedelta(days=15)
    token.created = now

    await db_session.commit()

    return token


async def delete_refresh_auth_token(db_session: AsyncSession, user: DBModelUser, token_id: str) -> AuthToken:
    token = await get_refresh_auth_token(db_session, user, token_id)

    if not token:
        raise HTTPException(status_code=404, detail="Refresh token not found or does not belong to the user.")

    await db_session.delete(token)
    await db_session.commit()


async def delete_refresh_auth_token_without_user(db_session: AsyncSession, token_id: str) -> AuthToken:
    token = await get_refresh_auth_token_without_user(db_session, token_id)

    if not token:
        raise HTTPException(status_code=404, detail="Refresh token not found or does not belong to the user.")

    await db_session.delete(token)
    await db_session.commit()


async def handle_refresh_token(
    db_session: AsyncSession, user: DBModelUser, refresh_token_id: Optional[str]
) -> AuthToken:
    if not refresh_token_id:
        return await create_refresh_auth_token(db_session, user)
    try:
        return await update_refresh_auth_token(db_session, user, refresh_token_id)
    except TokenInvalidError:
        await delete_refresh_auth_token_without_user(db_session, refresh_token_id)
        return await create_refresh_auth_token(db_session, user)