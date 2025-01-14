from fastapi import Response, BackgroundTasks, APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.services.auth import AuthService
from src.schemas.users import UserCreateModel
from src.settings import settings
from src.schemas.auth import (
    LoginModel,
    VerifyModel,
    ResponseSignupModel,
    ResponseLoginModel,
    ResponseVerifyModel,
)
from src.utils.exceptions import (
    bad_request_response_docs,
    unauthorized_response_docs,
    not_found_response_docs,
    conflict_response_docs,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/signup",
    status_code=status.HTTP_200_OK,
    response_model=ResponseSignupModel,
    responses={**bad_request_response_docs, **conflict_response_docs},
)
async def create_contact(
    background_tasks: BackgroundTasks,
    body: UserCreateModel,
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)
    await auth_service.signup(background_tasks, body)
    return {
        "message": "Registration successful. Please check your email to activate your account."
    }


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=ResponseLoginModel,
    responses={**bad_request_response_docs, **unauthorized_response_docs},
)
async def create_contact(
    response: Response,
    body: LoginModel,
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)
    access_token, refresh_token = await auth_service.login(body)
    response.set_cookie(
        "refresh_token",
        refresh_token,
        max_age=settings.JWT_REFRESH_EXPIRATION_SECONDS,
        httponly=True,
        secure=True,
    )
    return {"access_token": access_token}


@router.get(
    "/verify/{token}",
    status_code=status.HTTP_200_OK,
    response_model=ResponseVerifyModel,
    responses={
        **not_found_response_docs,
        **unauthorized_response_docs,
        **conflict_response_docs,
    },
)
async def verify_user(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)
    await auth_service.verify_user(token)
    return {
        "message": "Your email has been successfully verified. You can now log in to your account."
    }


@router.post(
    "/verify",
    status_code=status.HTTP_200_OK,
    response_model=ResponseVerifyModel,
    responses={
        **bad_request_response_docs,
        **not_found_response_docs,
        **conflict_response_docs,
    },
)
async def resend_verification_email(
    background_tasks: BackgroundTasks,
    body: VerifyModel,
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)
    await auth_service.resend_verification_email(background_tasks, body)
    return {"message": "Please check your email to activate your account."}
