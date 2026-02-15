from typing import Any
from uuid import UUID

from fastapi import Response
from httpx import AsyncClient
from loguru import logger
from sqlalchemy import select

from app.core.config import settings
from app.core.security import create_access_token
from app.core.tokens import (
    create_refresh_token_db,
    get_active_user_tokens,
    revoke_all_user_tokens,
    revoke_refresh_token,
    verify_refresh_token,
)
from app.exceptions import BadRequestError, NotFoundError, TokenExpiredError
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.user_repository import UserRepository


async def verify_google_token(token: str) -> dict[str, Any]:
    logger.debug("Verifying Google token")
    async with AsyncClient() as client:
        response = await client.get(
            f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
        )

        if response.status_code != 200:
            logger.error(
                f"Google token verification failed: status={response.status_code}"
            )
            raise BadRequestError(detail="Invalid Google token")

        google_info = response.json()

        if google_info["aud"] != settings.GOOGLE_CLIENT_ID:
            logger.error(
                f"Google Client ID mismatch: "
                f"expected={settings.GOOGLE_CLIENT_ID}, got={google_info['aud']}"
            )
            raise BadRequestError(detail="Invalid Google Client ID")

        logger.info(
            f"Google token verified successfully for email={google_info.get('email')}"
        )
        return google_info


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def authenticate_google_user(
        self, google_token: str, response: Response
    ) -> dict:
        logger.info("Authenticating Google user")
        google_info = await verify_google_token(google_token)
        email = google_info.get("email")
        if not email:
            logger.error("Email not found in Google token")
            raise BadRequestError(detail="Email not found in Google token")

        user = await self.user_repo.get_by_email(email)

        if not user:
            logger.info(f"Creating new user for email={email}")
            user = await self.user_repo.create(
                email=email,
                full_name=google_info.get("name"),
                is_active=True,
                is_superuser=False,
            )
            logger.success(f"New user created: id={user.id}, email={email}")
        else:
            logger.debug(f"Existing user found: id={user.id}, email={email}")

        access_token = create_access_token(subject=user.id)

        refresh_token_value = await create_refresh_token_db(
            self.user_repo.session, user.id
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token_value,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            path="/api/v1",
        )

        logger.success(f"Authentication successful for user_id={user.id}")
        return {
            "access_token": access_token,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.full_name or "",
                "created_at": user.created_at,
            },
        }

    async def refresh_access_token(self, refresh_token_value: str) -> dict:
        logger.info("Refreshing access token")

        db_token = await verify_refresh_token(
            self.user_repo.session, refresh_token_value
        )

        if not db_token:
            logger.error("Invalid or expired refresh token")
            raise TokenExpiredError(detail="Invalid or expired refresh token")

        result = await self.user_repo.session.execute(
            select(User).where(User.id == db_token.user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            logger.error(f"User not found for token user_id={db_token.user_id}")
            raise NotFoundError(resource="user")

        access_token = create_access_token(subject=user.id)

        logger.success(f"Access token refreshed for user_id={user.id}")
        return {"access_token": access_token}

    async def revoke_refresh_token(self, refresh_token_value: str):
        logger.info("Revoking refresh token")
        await revoke_refresh_token(self.user_repo.session, refresh_token_value)

    async def logout_all_devices(self, user_id: UUID) -> int:
        logger.info(f"Logging out all devices for user {user_id}")
        return await revoke_all_user_tokens(self.user_repo.session, user_id)

    async def get_active_sessions(self, user_id: UUID) -> list[RefreshToken]:
        logger.info(f"Fetching active sessions for user {user_id}")
        return await get_active_user_tokens(self.user_repo.session, user_id)
