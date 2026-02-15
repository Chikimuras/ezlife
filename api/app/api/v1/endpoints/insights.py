from datetime import date as date_type
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.insights_repository import InsightsRepository
from app.schemas.insights import DailyComparisonResponse, WeeklyComparisonResponse
from app.services.insights_service import InsightsService

router = APIRouter()


async def get_insights_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> InsightsService:
    return InsightsService(insights_repo=InsightsRepository(db))


@router.get("/weekly-comparison", response_model=WeeklyComparisonResponse)
async def get_weekly_comparison(
    service: Annotated[InsightsService, Depends(get_insights_service)],
    current_user: Annotated[User, Depends(get_current_user)],
    date: Annotated[date_type | None, Query()] = None,
):
    target_date = date if date else date_type.today()
    result = await service.get_weekly_comparison(current_user.id, target_date)
    return result


@router.get("/daily-comparison", response_model=DailyComparisonResponse)
async def get_daily_comparison(
    service: Annotated[InsightsService, Depends(get_insights_service)],
    current_user: Annotated[User, Depends(get_current_user)],
    date: Annotated[date_type | None, Query()] = None,
):
    target_date = date if date else date_type.today()
    result = await service.get_daily_comparison(current_user.id, target_date)
    return result
