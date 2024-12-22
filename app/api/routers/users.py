from uuid import UUID

from fastapi import APIRouter, Depends, Request, HTTPException
from typing import Annotated, List

from app.api.dependencies.auth import validate_is_authenticated, validate_password_reset
from app.api.dependencies.user import CurrentUserDep, CurrentAdminDep
from app.api.dependencies.core import DBSessionDep
from app.crud.log import create_log
from app.crud.sales_receipt import create_sales_receipt
from app.crud.sales_receipt_products import create_sales_receipt_product
from app.crud.user import (update_user_profile, create_password_token, create_new_password)
from app.schemas.sales_receipt import CreateSalesReceipt
from app.schemas.sales_receipt_products import CreateSalesReceiptProduct

from app.schemas.user import (User, AuthorizedUser, UpdateProfile, ResetPasswordArgs)

router = APIRouter(
    prefix="/api/users",
    tags=["users"],
    responses={404: {"description": "Not found"}}
)


@router.get(
    "/me",
    response_model=AuthorizedUser
)
async def user_details(current_user: CurrentUserDep, db_session: DBSessionDep):
    await create_log(db_session, "me", current_user)
    return current_user


@router.patch(
    "/change/profile",
    response_model=AuthorizedUser
)
async def change_profile(
        profile_update: UpdateProfile,
        current_user: CurrentUserDep,
        db_session: DBSessionDep
):
    print(profile_update)
    try:
        updated_user = await update_user_profile(db_session, current_user, profile_update)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    await create_log(db_session, "change_profile", current_user)
    return updated_user


@router.post(
    "/make/password_reset_token"
)
async def make_password_reset_token(
        current_user: CurrentUserDep,
        db_session: DBSessionDep
):
    user = await create_password_token(db_session, current_user)
    await create_log(db_session, "make_password_reset_token", current_user)
    return "Create success new password token"


@router.post(
    "/reset_password",
)
async def reset_password(
        reset_password_args: ResetPasswordArgs,
        db_session: DBSessionDep,
        current_user: User = Depends(validate_password_reset),
):
    user = await create_new_password(db_session, current_user, reset_password_args)

    await create_log(db_session, "reset_password", current_user)

    return {"Success": True}


@router.get(
    "/admin",
    response_model=AuthorizedUser
)
async def user_details(current_admin: CurrentAdminDep):
    return current_admin

@router.post("/receipt")
async def create_receipt(current_user: CurrentUserDep, db_session: DBSessionDep):
    new_receipt = await create_sales_receipt(db_session, current_user.id)
    return new_receipt


@router.post("/product")
async def create_product(
        current_user: CurrentUserDep,
        product: CreateSalesReceiptProduct,
        db_session: DBSessionDep
):
    new_product = await create_sales_receipt_product(db_session, product, UUID("ae897f62-de4f-4059-ae5f-f83e315f7c7d"))
    return new_product
