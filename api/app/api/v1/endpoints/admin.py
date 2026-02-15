from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cleanup import cleanup_expired_tokens
from app.db.session import get_db

router = APIRouter()


class CleanupResponse(BaseModel):
    message: str
    deleted_count: int


@router.post("/admin/cleanup-tokens", response_model=CleanupResponse)
async def cleanup_tokens_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    deleted_count = await cleanup_expired_tokens(db)
    return {"message": "Token cleanup completed", "deleted_count": deleted_count}
