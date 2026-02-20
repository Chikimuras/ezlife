from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.activity_repository import (
    ActivityRepository,
    CategoryRepository,
    GlobalConstraintsRepository,
    GroupRepository,
)
from app.repositories.task_repository import (
    TaskActivityRepository,
    TaskListRepository,
    TaskRepository,
)
from app.schemas.task import (
    ConvertToActivityRequest,
    TaskActivityResponse,
    TaskCompleteRequest,
    TaskCreate,
    TaskListCreate,
    TaskListResponse,
    TaskListUpdate,
    TaskResponse,
    TaskUpdate,
)
from app.services.activity_service import ActivityService
from app.services.task_service import TaskService

router = APIRouter()


def _to_task_response(task) -> TaskResponse:
    task_response = TaskResponse.model_validate(task)
    task_response.activity_ids = [
        ta.activity_id for ta in (task.task_activities or [])
    ]
    return task_response


async def get_task_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskService:
    activity_service = ActivityService(
        group_repo=GroupRepository(db),
        category_repo=CategoryRepository(db),
        constraints_repo=GlobalConstraintsRepository(db),
        activity_repo=ActivityRepository(db),
    )
    return TaskService(
        task_list_repo=TaskListRepository(db),
        task_repo=TaskRepository(db),
        task_activity_repo=TaskActivityRepository(db),
        activity_service=activity_service,
    )


@router.get("/task-lists", response_model=list[TaskListResponse])
async def list_task_lists(
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await service.get_task_lists(current_user.id)


@router.post(
    "/task-lists", response_model=TaskListResponse, status_code=status.HTTP_201_CREATED
)
async def create_task_list(
    data: TaskListCreate,
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await service.create_task_list(data, current_user.id)


@router.put("/task-lists/{id}", response_model=TaskListResponse)
async def update_task_list(
    id: UUID,
    data: TaskListUpdate,
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await service.update_task_list(id, data, current_user.id)


@router.delete("/task-lists/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_list(
    id: UUID,
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    await service.delete_task_list(id, current_user.id)


@router.get("/tasks", response_model=list[TaskResponse])
async def list_tasks(
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(get_current_user)],
    list_id: UUID | None = None,
    status: str | None = None,
):
    tasks = await service.get_tasks(current_user.id, list_id=list_id, status=status)
    return [_to_task_response(task) for task in tasks]


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskCreate,
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    task = await service.create_task(data, current_user.id)
    return _to_task_response(task)


@router.get("/tasks/{id}", response_model=TaskResponse)
async def get_task(
    id: UUID,
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    task = await service.get_task(id, current_user.id)
    return _to_task_response(task)


@router.put("/tasks/{id}", response_model=TaskResponse)
async def update_task(
    id: UUID,
    data: TaskUpdate,
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    task = await service.update_task(id, data, current_user.id)
    return _to_task_response(task)


@router.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    id: UUID,
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    await service.delete_task(id, current_user.id)


@router.post(
    "/tasks/{id}/generate-occurrences",
    response_model=list[TaskResponse],
    status_code=status.HTTP_201_CREATED,
)
async def generate_occurrences(
    id: UUID,
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(get_current_user)],
    count: int = Query(default=10, ge=1, le=52),
):
    tasks = await service.generate_occurrences(id, current_user.id, count)
    return [_to_task_response(task) for task in tasks]


@router.post("/tasks/generate-rolling", response_model=dict)
async def generate_rolling_occurrences(
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    result = await service.generate_rolling_occurrences(current_user.id)
    return {
        "createdCount": result["created_count"],
        "recurringTasksChecked": result["recurring_tasks_checked"],
        "note": "Call this endpoint from an external scheduler/cron job.",
    }


@router.post("/tasks/{id}/complete", response_model=TaskResponse)
async def complete_task(
    id: UUID,
    data: TaskCompleteRequest,
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    task = await service.complete_task(id, current_user.id, data)
    return _to_task_response(task)


@router.post(
    "/tasks/{id}/convert-to-activity",
    response_model=TaskActivityResponse,
    status_code=status.HTTP_201_CREATED,
)
async def convert_task_to_activity(
    id: UUID,
    data: ConvertToActivityRequest,
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await service.convert_task_to_activity(id, current_user.id, data)
