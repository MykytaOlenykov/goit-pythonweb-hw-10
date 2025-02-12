from fastapi import Depends, Header, HTTPException, status
from fastapi.security.utils import get_authorization_scheme_param
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from src.database.db import get_db
from src.services.users import UsersService
from src.schemas.tokens import BaseTokenPayloadModel
from src.utils.tokens import decode_jwt


async def authenticate(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    scheme, token = get_authorization_scheme_param(authorization)

    if not (authorization and scheme and token):
        raise credentials_exception

    if scheme != "Bearer" or not token:
        raise credentials_exception

    try:
        payload = decode_jwt(token) or {}
        verified_payload = BaseTokenPayloadModel(**payload)
    except ValidationError:
        raise credentials_exception

    users_service = UsersService(db)
    user = await users_service.get_by_id_or_none(id=verified_payload.user_id)

    if not user:
        raise credentials_exception

    return user
