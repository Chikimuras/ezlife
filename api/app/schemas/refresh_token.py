from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.base import CamelModel


class RefreshTokenCreate(CamelModel):
    token: str
    user_id: UUID
    expires_at: datetime


class RefreshTokenResponse(CamelModel):
    id: int
    user_id: UUID
    expires_at: datetime
    created_at: datetime
    revoked: bool


class ActiveSessionResponse(CamelModel):
    id: int
    created_at: datetime
    expires_at: datetime


class ActiveSessionsListResponse(BaseModel):
    sessions: list[ActiveSessionResponse]
    total: int


class LogoutAllDevicesResponse(BaseModel):
    message: str
    revoked_count: int
