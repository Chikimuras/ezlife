import re
from datetime import date, datetime, time
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from loguru import logger
from pydantic import field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.exceptions import ConflictError, NotFoundError
from app.models.activity import Activity, Category
from app.models.user import User
from app.schemas.activity import ActivityResponse
from app.schemas.base import CamelModel

router = APIRouter()


class TimerStartRequest(CamelModel):
    category_id: UUID


class TimerStopAtRequest(CamelModel):
    end_time: time

    @field_validator("end_time", mode="before")
    @classmethod
    def validate_time_format(cls, v: str | time | None) -> time | None:
        if isinstance(v, time):
            return v
        if isinstance(v, str):
            if not re.match(r"^([01]\d|2[0-3]):([0-5]\d)$", v):
                raise ValueError("Time must be in HH:mm format")
            hours, minutes = v.split(":")
            return time(int(hours), int(minutes))
        return v


async def _get_active_timer(db: AsyncSession, user_id: UUID) -> Activity | None:
    result = await db.execute(
        select(Activity).where(
            Activity.user_id == user_id,
            Activity.end_time.is_(None),
        )
    )
    return result.scalar_one_or_none()


@router.post(
    "/start",
    response_model=ActivityResponse,
    status_code=status.HTTP_201_CREATED,
)
async def start_timer(
    data: TimerStartRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ActivityResponse:
    active = await _get_active_timer(db, current_user.id)
    if active is not None:
        logger.warning(f"Timer already running for user_id={current_user.id}")
        raise ConflictError(
            code="CONFLICT_003",
            message="Timer already running",
            detail="Stop the current timer before " "starting a new one",
        )

    result = await db.execute(
        select(Category).where(
            Category.id == data.category_id,
            Category.user_id == current_user.id,
        )
    )
    category = result.scalar_one_or_none()
    if category is None:
        logger.warning(
            f"Category {data.category_id} not found " f"for user_id={current_user.id}"
        )
        raise NotFoundError(
            resource="category",
            resource_id=str(data.category_id),
        )

    now_time = datetime.now().time().replace(second=0, microsecond=0)
    activity = Activity(
        user_id=current_user.id,
        category_id=data.category_id,
        date=date.today(),
        start_time=now_time,
        end_time=None,
    )
    db.add(activity)
    await db.commit()
    await db.refresh(activity)

    logger.info(
        f"Timer started for user_id={current_user.id}, "
        f"category_id={data.category_id}"
    )
    return ActivityResponse.model_validate(activity)


@router.post("/stop", response_model=ActivityResponse)
async def stop_timer(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ActivityResponse:
    activity = await _get_active_timer(db, current_user.id)
    if activity is None:
        logger.warning(f"No active timer for user_id={current_user.id}")
        raise NotFoundError(
            resource="timer",
            detail="No active timer found",
        )

    activity.end_time = datetime.now().time().replace(second=0, microsecond=0)
    await db.commit()
    await db.refresh(activity)

    logger.info(
        f"Timer stopped for user_id={current_user.id}, " f"activity_id={activity.id}"
    )
    return ActivityResponse.model_validate(activity)


@router.post("/stop-at", response_model=ActivityResponse)
async def stop_timer_at(
    data: TimerStopAtRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ActivityResponse:
    activity = await _get_active_timer(db, current_user.id)
    if activity is None:
        logger.warning(f"No active timer for user_id={current_user.id}")
        raise NotFoundError(
            resource="timer",
            detail="No active timer found",
        )

    activity.end_time = data.end_time
    await db.commit()
    await db.refresh(activity)

    logger.info(f"Timer stopped at {data.end_time} " f"for user_id={current_user.id}")
    return ActivityResponse.model_validate(activity)


@router.get("/active", response_model=ActivityResponse)
async def get_active_timer(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ActivityResponse:
    activity = await _get_active_timer(db, current_user.id)
    if activity is None:
        logger.info(f"No active timer for user_id={current_user.id}")
        raise NotFoundError(
            resource="timer",
            detail="No active timer found",
        )
    return ActivityResponse.model_validate(activity)
