"""Background cleanup tasks for database maintenance."""

from datetime import datetime

from loguru import logger
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken


async def cleanup_expired_tokens(db: AsyncSession) -> int:
    """
    Delete expired and revoked refresh tokens from the database.

    Args:
        db: Database session

    Returns:
        Number of tokens deleted
    """
    logger.info("Starting cleanup of expired refresh tokens")

    from sqlalchemy import select

    tokens_to_delete = await db.execute(
        select(RefreshToken).where(
            (RefreshToken.expires_at < datetime.utcnow())
            | (RefreshToken.revoked == True)  # noqa: E712
        )
    )
    tokens_list = list(tokens_to_delete.scalars().all())
    count = len(tokens_list)

    await db.execute(
        delete(RefreshToken).where(
            (RefreshToken.expires_at < datetime.utcnow())
            | (RefreshToken.revoked == True)  # noqa: E712
        )
    )

    await db.commit()

    logger.success(f"Cleanup completed: {count} expired/revoked tokens removed")
    return count
