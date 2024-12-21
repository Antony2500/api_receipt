import logging
from datetime import timedelta

import jwt
from fastapi import APIRouter, Depends, Request, HTTPException

from app.crud.log import create_log
from app.schemas.auth import TokenData
from app.api.dependencies.core import DBSessionDep
from app.api.dependencies.user import CurrentUserDep, CurrentRefreshDataUser
from app.api.dependencies.auth import validate_signup, validate_login, validate_is_authenticated
from app.schemas.auth import Signup, Token, TokenInfo, LoginValidationResult
from app.crud.user import create_user, get_user_by_email
from app.crud.auth import create_refresh_auth_token, update_refresh_auth_token, delete_refresh_auth_token, \
    handle_refresh_token, get_refresh_auth_token, get_refresh_auth_token_without_user
from app.models.user import User
from app.constants import REFRESH_TOKEN_TYPE
from app.services.auth import create_access_token, create_refresh_token, get_token_payload, validate_token_type

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/registration",
    summary="Signup",
)
async def signup(
        request: Request,
        db_session: DBSessionDep,
        signup: Signup = Depends(validate_signup),
):
    user = await create_user(db_session, signup)

    refresh_token = await create_refresh_auth_token(db_session, user)
    access_token = create_access_token(user, refresh_token)

    request.session["access_token"] = access_token

    await create_log(db_session, "signup", user)

    return {
        "user_id": user.id,
        "user_name": user.username,
        "time_creation": user.created
    }


@router.post(
    "/login",
    summary="Login"
)
async def login(
        request: Request,
        db_session: DBSessionDep,
        login_result: LoginValidationResult = Depends(validate_login)
):
    user = login_result.user
    refresh_token_id = login_result.refresh_token_id

    refresh_token = await handle_refresh_token(db_session, user, refresh_token_id)

    access_token = create_access_token(user, refresh_token)
    request.session["access_token"] = access_token

    await create_log(db_session, "login", user)

    return TokenInfo(access_token=access_token)


@router.post(
    "/logout",
)
async def logout(
        request: Request,
        db_session: DBSessionDep,
        refresh_data: CurrentRefreshDataUser
):
    user = refresh_data.user
    refresh_token_id = refresh_data.refresh_token_id

    await delete_refresh_auth_token(db_session, user, refresh_token_id)
    del request.session["access_token"]

    await create_log(db_session, "refresh", None)
    return "Logout successful"


@router.post(
    "/refresh"
)
async def auth_refresh_token(
        request: Request,
        db_session: DBSessionDep,
        refresh_data: CurrentRefreshDataUser
):
    try:
        refresh_token = await update_refresh_auth_token(db_session, refresh_data.user, refresh_data.refresh_token_id)
        access_token = create_access_token(refresh_data.user, refresh_token)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail="Invalid refresh token.")

    request.session["access_token"] = access_token

    await create_log(db_session, "refresh", refresh_data.user)

    return access_token