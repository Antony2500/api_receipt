import logging
from fastapi import HTTPException, Request

from app.schemas.auth import Signup, LoginArgs, LoginValidationResult
from app.models.user import User
from app.crud.user import get_user_by_username, get_user_by_email
from app.errors import Abort
from app.constants import ACCESS_TOKEN_TYPE
from app.utils.auth import verify_password, is_protected_username, utc_now
from app.services.auth import check_auth_user_from_token_by_payload, get_token_payload

from .user import CurrentUserDep
from .core import DBSessionDep


logging.basicConfig(level=logging.DEBUG)


async def validate_is_authenticated(current_user: CurrentUserDep) -> User:
    return current_user


async def validate_signup(signup: Signup, db_session: DBSessionDep) -> Signup:
    """
    Validates the signup data' user.

    :param signup: The signup data to be validate.
    :type signup: Pydantic schema Signup

    :param db_session: The database session dependency.

    :return: Signup: The validated signup data.

    :raise:
        HTTPException: If the username is invalid, already exists,
            or if the email already exists.
    """
    logging.debug(f"Validating signup data: {signup}")
    if is_protected_username(signup.username):
        logging.debug(f"Invalid username detected: {signup.username}")
        raise HTTPException(status_code=400, detail="Invalid username")

    if await get_user_by_username(db_session, signup.username):
        logging.debug(f"Username already exists: {signup.username}")
        raise HTTPException(status_code=400, detail="Username already exists")

    if await get_user_by_email(db_session, signup.email):
        logging.debug(f"Email already    exists: {signup.email}")
        raise HTTPException(status_code=400, detail="Email already exists")

    return signup


async def validate_login(
        request: Request,
        login: LoginArgs,
        db_session: DBSessionDep
) -> LoginValidationResult:
    if not (user := await get_user_by_email(db_session, login.email)):
        raise HTTPException(status_code=401, detail="user-not-found")

    if not verify_password(login.password, user.hashed_password):
        raise Abort("auth", "invalid-password")

    refresh_token_id = None

    access_token = request.session.get("access_token")
    if access_token:
        payload = get_token_payload(token=access_token, check_expired_token=False)
        print(payload)
        refresh_token_id = payload.get("refresh_token_id")
        print(refresh_token_id)
        # if not check_auth_user_from_token_by_payload(ACCESS_TOKEN_TYPE, login.email, payload):
        #     root_logger.warning(f"Invalid access token for user {login.email}. Refresh token ID: {refresh_token_id}")



    return LoginValidationResult(user=user, refresh_token_id=refresh_token_id)



def validate_password_reset(
        current_user: CurrentUserDep
) -> User:
    if current_user.password_reset_expire:

        print(utc_now(), current_user.password_reset_expire)
        if utc_now() > current_user.password_reset_expire:
            raise Abort("auth", "reset-valid")

    return current_user

