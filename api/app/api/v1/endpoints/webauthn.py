"""WebAuthn / passkeys endpoints.

Handles passkey-based registration and authentication ceremonies and
passkey management for authenticated users.
"""

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Cookie, Depends, Response, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.api.v1.endpoints.auth import LoginResponse
from app.core.webauthn_challenge import CHALLENGE_COOKIE_NAME
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.base import CamelModel
from app.services.webauthn_service import WebAuthnService

router = APIRouter()


# ----------------------------------------------------------------------
# Request schemas
# ----------------------------------------------------------------------
class RegisterOptionsRequest(CamelModel):
    email: EmailStr
    name: str


class VerifyRequest(CamelModel):
    credential: dict[str, Any]


# ----------------------------------------------------------------------
# Response schemas
# ----------------------------------------------------------------------
class PasskeySummary(CamelModel):
    id: UUID
    device_name: str | None
    created_at: Any  # datetime serialised as ISO string
    last_used_at: Any | None


class PasskeyListResponse(CamelModel):
    passkeys: list[PasskeySummary]


class PasskeyCreatedResponse(CamelModel):
    passkey: PasskeySummary


# ----------------------------------------------------------------------
# Registration ceremony (anonymous)
# ----------------------------------------------------------------------
@router.post("/auth/register/options")
async def register_options(
    payload: RegisterOptionsRequest,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    user_repo = UserRepository(db)
    service = WebAuthnService(user_repo)
    return await service.begin_registration(payload.email, payload.name, response)


@router.post("/auth/register/verify", response_model=LoginResponse)
async def register_verify(
    payload: VerifyRequest,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    webauthn_challenge: Annotated[
        str | None, Cookie(alias=CHALLENGE_COOKIE_NAME)
    ] = None,
):
    user_repo = UserRepository(db)
    service = WebAuthnService(user_repo)
    return await service.finish_registration(
        payload.credential, webauthn_challenge, response
    )


# ----------------------------------------------------------------------
# Authentication ceremony (anonymous, usernameless)
# ----------------------------------------------------------------------
@router.post("/auth/login/options")
async def login_options(
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    user_repo = UserRepository(db)
    service = WebAuthnService(user_repo)
    return await service.begin_authentication(response)


@router.post("/auth/login/verify", response_model=LoginResponse)
async def login_verify(
    payload: VerifyRequest,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    webauthn_challenge: Annotated[
        str | None, Cookie(alias=CHALLENGE_COOKIE_NAME)
    ] = None,
):
    user_repo = UserRepository(db)
    service = WebAuthnService(user_repo)
    return await service.finish_authentication(
        payload.credential, webauthn_challenge, response
    )


# ----------------------------------------------------------------------
# Passkey management (authenticated)
# ----------------------------------------------------------------------
@router.get("/auth/passkeys", response_model=PasskeyListResponse)
async def list_passkeys(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user_repo = UserRepository(db)
    service = WebAuthnService(user_repo)
    passkeys = await service.list_passkeys(current_user.id)
    return {
        "passkeys": [
            {
                "id": p.id,
                "device_name": p.device_name,
                "created_at": p.created_at,
                "last_used_at": p.last_used_at,
            }
            for p in passkeys
        ]
    }


@router.post("/auth/passkeys/options")
async def add_passkey_options(
    current_user: Annotated[User, Depends(get_current_user)],
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    user_repo = UserRepository(db)
    service = WebAuthnService(user_repo)
    return await service.begin_add_passkey(current_user, response)


@router.post("/auth/passkeys/verify", response_model=PasskeyCreatedResponse)
async def add_passkey_verify(
    payload: VerifyRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    webauthn_challenge: Annotated[
        str | None, Cookie(alias=CHALLENGE_COOKIE_NAME)
    ] = None,
):
    user_repo = UserRepository(db)
    service = WebAuthnService(user_repo)
    cred = await service.finish_add_passkey(
        current_user, payload.credential, webauthn_challenge, response
    )
    return {
        "passkey": {
            "id": cred.id,
            "device_name": cred.device_name,
            "created_at": cred.created_at,
            "last_used_at": cred.last_used_at,
        }
    }


@router.delete("/auth/passkeys/{passkey_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_passkey(
    passkey_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
    user_repo = UserRepository(db)
    service = WebAuthnService(user_repo)
    await service.delete_passkey(current_user, passkey_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
