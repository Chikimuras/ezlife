from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Response
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.exceptions import BadRequestError
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.refresh_token import (
    ActiveSessionsListResponse,
    LogoutAllDevicesResponse,
)
from app.services.auth_service import AuthService

router = APIRouter()


class UserInToken(BaseModel):
    id: str
    email: EmailStr
    name: str
    created_at: datetime | None = None


class LoginResponse(BaseModel):
    access_token: str
    user: UserInToken


class RefreshResponse(BaseModel):
    access_token: str


class MeResponse(BaseModel):
    user: UserInToken


class LogoutResponse(BaseModel):
    message: str


class GoogleToken(BaseModel):
    token: str


@router.post("/login/google", response_model=LoginResponse)
async def login_google(
    token_data: GoogleToken,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    return await auth_service.authenticate_google_user(token_data.token, response)


@router.post("/auth/refresh", response_model=RefreshResponse)
async def refresh_token(
    db: Annotated[AsyncSession, Depends(get_db)],
    refresh_token: Annotated[str | None, Cookie(alias="refresh_token")] = None,
):
    if not refresh_token:
        raise BadRequestError(detail="Refresh token missing")

    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    return await auth_service.refresh_access_token(refresh_token)


@router.get("/auth/me", response_model=MeResponse)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    return {
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "name": current_user.full_name or "",
            "created_at": current_user.created_at,
        }
    }


@router.post("/auth/logout", response_model=LogoutResponse)
async def logout(
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    refresh_token: Annotated[str | None, Cookie(alias="refresh_token")] = None,
):
    if refresh_token:
        user_repo = UserRepository(db)
        auth_service = AuthService(user_repo)
        await auth_service.revoke_refresh_token(refresh_token)

    response.delete_cookie(
        key="refresh_token",
        path="/api/v1",
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
    )

    return {"message": "Logged out successfully"}


@router.post("/auth/logout-all", response_model=LogoutAllDevicesResponse)
async def logout_all_devices(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    revoked_count = await auth_service.logout_all_devices(current_user.id)

    return {
        "message": "All devices logged out successfully",
        "revoked_count": revoked_count,
    }


@router.get("/auth/sessions", response_model=ActiveSessionsListResponse)
async def get_active_sessions(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    sessions = await auth_service.get_active_sessions(current_user.id)

    return {
        "sessions": [
            {"id": s.id, "created_at": s.created_at, "expires_at": s.expires_at}
            for s in sessions
        ],
        "total": len(sessions),
    }
