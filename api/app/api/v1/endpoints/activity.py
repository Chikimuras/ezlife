from datetime import date as date_type
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.activity import Activity
from app.models.task import Task, TaskActivity
from app.models.user import User
from app.repositories.activity_repository import (
    ActivityRepository,
    CategoryRepository,
    GroupRepository,
)
from app.schemas.activity import (
    ActivityCreate,
    ActivityResponse,
    ActivityUpdate,
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    GroupCreate,
    GroupResponse,
    GroupUpdate,
)
from app.services.activity_service import ActivityService

router = APIRouter()


async def get_activity_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ActivityService:
    return ActivityService(
        group_repo=GroupRepository(db),
        category_repo=CategoryRepository(db),
        activity_repo=ActivityRepository(db),
    )


async def _enrich_with_task_info(
    activities: list[Activity], db: AsyncSession
) -> list[ActivityResponse]:
    if not activities:
        return []

    activity_ids = [activity.id for activity in activities]

    result = await db.execute(
        select(TaskActivity).where(TaskActivity.activity_id.in_(activity_ids))
    )
    task_activity_links = {
        link.activity_id: link.task_id for link in result.scalars().all()
    }

    task_ids = list(task_activity_links.values())
    tasks_dict: dict[UUID, Task] = {}
    if task_ids:
        result = await db.execute(
            select(Task)
            .options(selectinload(Task.task_list))
            .where(Task.id.in_(task_ids))
        )
        tasks_dict = {task.id: task for task in result.scalars().all()}

    enriched: list[ActivityResponse] = []
    for activity in activities:
        response = ActivityResponse.model_validate(activity)
        task_id = task_activity_links.get(activity.id)
        if task_id is not None:
            task = tasks_dict.get(task_id)
            if task is not None:
                response.task_name = task.title
                response.task_id = str(task.id)
                response.is_from_task = True
                if task.task_list is not None:
                    response.task_list_color = task.task_list.color
        enriched.append(response)

    return enriched


@router.get("/groups", response_model=list[GroupResponse])
async def list_groups(
    service: Annotated[ActivityService, Depends(get_activity_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await service.get_groups(current_user.id)


@router.get("/groups/{id}", response_model=GroupResponse)
async def get_group(
    id: UUID,
    service: Annotated[ActivityService, Depends(get_activity_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await service.get_group(id, current_user.id)


@router.post(
    "/groups", response_model=GroupResponse, status_code=status.HTTP_201_CREATED
)
async def create_group(
    data: GroupCreate,
    service: Annotated[ActivityService, Depends(get_activity_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await service.create_group(data, current_user.id)


@router.patch("/groups/{id}", response_model=GroupResponse)
async def update_group(
    id: UUID,
    data: GroupUpdate,
    service: Annotated[ActivityService, Depends(get_activity_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await service.update_group(id, data, current_user.id)


@router.delete("/groups/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    id: UUID,
    service: Annotated[ActivityService, Depends(get_activity_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    await service.delete_group(id, current_user.id)


@router.get("/categories", response_model=list[CategoryResponse])
async def list_categories(
    service: Annotated[ActivityService, Depends(get_activity_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await service.get_categories(current_user.id)


@router.get("/categories/{id}", response_model=CategoryResponse)
async def get_category(
    id: UUID,
    service: Annotated[ActivityService, Depends(get_activity_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await service.get_category(id, current_user.id)


@router.post(
    "/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED
)
async def create_category(
    data: CategoryCreate,
    service: Annotated[ActivityService, Depends(get_activity_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await service.create_category(data, current_user.id)


@router.patch("/categories/{id}", response_model=CategoryResponse)
async def update_category(
    id: UUID,
    data: CategoryUpdate,
    service: Annotated[ActivityService, Depends(get_activity_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await service.update_category(id, data, current_user.id)


@router.delete("/categories/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    id: UUID,
    service: Annotated[ActivityService, Depends(get_activity_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    await service.delete_category(id, current_user.id)


@router.get("/activities", response_model=list[ActivityResponse])
async def list_activities(
    service: Annotated[ActivityService, Depends(get_activity_service)],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    activities = await service.get_activities(current_user.id)
    return await _enrich_with_task_info(activities, db)


@router.get("/activities/date/{date}", response_model=list[ActivityResponse])
async def list_activities_by_date(
    date: date_type,
    service: Annotated[ActivityService, Depends(get_activity_service)],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    activities = await service.get_activities_by_date(current_user.id, date)
    return await _enrich_with_task_info(activities, db)


@router.get("/activities/{id}", response_model=ActivityResponse)
async def get_activity_by_id(
    id: UUID,
    service: Annotated[ActivityService, Depends(get_activity_service)],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    activity = await service.get_activity(id, current_user.id)
    enriched_activities = await _enrich_with_task_info([activity], db)
    return enriched_activities[0]


@router.post(
    "/activities", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED
)
async def create_activity(
    data: ActivityCreate,
    service: Annotated[ActivityService, Depends(get_activity_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await service.create_activity(data, current_user.id)


@router.put("/activities/{id}", response_model=ActivityResponse)
async def update_activity(
    id: UUID,
    data: ActivityUpdate,
    service: Annotated[ActivityService, Depends(get_activity_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await service.update_activity(id, data, current_user.id)


@router.delete("/activities/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(
    id: UUID,
    service: Annotated[ActivityService, Depends(get_activity_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    await service.delete_activity(id, current_user.id)
