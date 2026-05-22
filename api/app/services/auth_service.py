from uuid import UUID

from loguru import logger
from sqlalchemy import select

from app.core.security import create_access_token
from app.core.tokens import (
    get_active_user_tokens,
    revoke_all_user_tokens,
    revoke_refresh_token,
    verify_refresh_token,
)
from app.exceptions import NotFoundError, TokenExpiredError
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

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
