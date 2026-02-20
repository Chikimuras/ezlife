from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.cleanup import cleanup_expired_tokens
from app.db.session import get_db
from app.models.user import User

router = APIRouter()


class CleanupResponse(BaseModel):
    message: str
    deleted_count: int


@router.post("/admin/cleanup-tokens", response_model=CleanupResponse)
async def cleanup_tokens_endpoint(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if not current_user.is_superuser:
        logger.warning(f"Non-admin user {current_user.id} attempted admin endpoint")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    deleted_count = await cleanup_expired_tokens(db)
    return {"message": "Token cleanup completed", "deleted_count": deleted_count}
