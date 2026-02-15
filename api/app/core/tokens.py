import hashlib
import secrets
from datetime import datetime, timedelta
from uuid import UUID

from jose import JWTError, jwt
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.refresh_token import RefreshToken


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        return None


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(64)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


async def create_refresh_token_db(db: AsyncSession, user_id: UUID) -> str:
    raw_token = generate_refresh_token()
    hashed = hash_token(raw_token)

    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    db_token = RefreshToken(
        token=hashed,
        user_id=user_id,
        expires_at=expires_at,
    )
    db.add(db_token)
    await db.commit()

    logger.info(f"Created refresh token for user {user_id}")
    return raw_token


async def verify_refresh_token(db: AsyncSession, raw_token: str) -> RefreshToken | None:
    hashed = hash_token(raw_token)
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token == hashed,
            RefreshToken.revoked == False,  # noqa: E712
            RefreshToken.expires_at > datetime.utcnow(),
        )
    )
    token = result.scalar_one_or_none()

    if token:
        logger.debug(f"Verified refresh token for user {token.user_id}")
    else:
        logger.warning("Refresh token verification failed")

    return token


async def revoke_refresh_token(db: AsyncSession, raw_token: str):
    hashed = hash_token(raw_token)
    result = await db.execute(select(RefreshToken).where(RefreshToken.token == hashed))
    token = result.scalar_one_or_none()

    if token:
        token.revoked = True
        await db.commit()
        logger.info(f"Revoked refresh token for user {token.user_id}")


async def revoke_all_user_tokens(db: AsyncSession, user_id: UUID) -> int:
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked == False,  # noqa: E712
        )
    )
    tokens = result.scalars().all()

    count = 0
    for token in tokens:
        token.revoked = True
        count += 1

    await db.commit()
    logger.info(f"Revoked {count} refresh tokens for user {user_id}")
    return count


async def get_active_user_tokens(db: AsyncSession, user_id: UUID) -> list[RefreshToken]:
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked == False,  # noqa: E712
            RefreshToken.expires_at > datetime.utcnow(),
        )
    )
    return list(result.scalars().all())
