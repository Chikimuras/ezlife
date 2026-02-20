import uuid
from datetime import date, time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.exc import IntegrityError

from app.exceptions import BadRequestError, DependencyConflictError, NotFoundError
from app.repositories.task_repository import (
    TaskActivityRepository,
    TaskListRepository,
    TaskRepository,
)
from app.schemas.task import (
    ConvertToActivityRequest,
    TaskCompleteRequest,
    TaskCreate,
    TaskListCreate,
    TaskListUpdate,
    TaskUpdate,
)
from app.services.activity_service import ActivityService
from app.services.task_service import TaskService


def make_task_mock(**overrides):
    defaults = {
        "id": uuid.uuid4(),
        "category_id": uuid.uuid4(),
        "title": "Task title",
        "priority": "medium",
        "position": 0,
        "scheduled_date": date(2026, 1, 10),
        "scheduled_start_time": time(9, 0),
        "scheduled_end_time": time(10, 0),
        "estimated_duration_minutes": 60,
        "description": "Task description",
        "recurrence_rule": None,
        "exception_dates": None,
        "status": "todo",
        "task_list_id": uuid.uuid4(),
        "task_activities": [],
    }
    defaults.update(overrides)
    return MagicMock(**defaults)


@pytest.fixture
def task_list_repo():
    return AsyncMock(spec=TaskListRepository)


@pytest.fixture
def task_repo():
    return AsyncMock(spec=TaskRepository)


@pytest.fixture
def task_activity_repo():
    return AsyncMock(spec=TaskActivityRepository)


@pytest.fixture
def activity_service():
    service = AsyncMock(spec=ActivityService)
    service.create_activity = AsyncMock()
    service.get_category = AsyncMock()
    return service


@pytest.fixture
def task_service(task_list_repo, task_repo, task_activity_repo, activity_service):
    return TaskService(task_list_repo, task_repo, task_activity_repo, activity_service)


@pytest.mark.asyncio
async def test_get_task_lists_returns_lists(task_service, task_list_repo):
    user_id = uuid.uuid4()
    task_lists = [MagicMock(id=uuid.uuid4(), user_id=user_id, name="Inbox")]
    task_list_repo.get_by_user.return_value = task_lists

    result = await task_service.get_task_lists(user_id)

    assert result == task_lists
    task_list_repo.get_by_user.assert_awaited_once_with(user_id)


@pytest.mark.asyncio
async def test_get_task_list_returns_task_list(task_service, task_list_repo):
    task_list_id = uuid.uuid4()
    user_id = uuid.uuid4()
    task_list = MagicMock(id=task_list_id, user_id=user_id, name="Work")
    task_list_repo.get_by_id_and_user.return_value = task_list

    result = await task_service.get_task_list(task_list_id, user_id)

    assert result == task_list
    task_list_repo.get_by_id_and_user.assert_awaited_once_with(task_list_id, user_id)


@pytest.mark.asyncio
async def test_get_task_list_raises_not_found_when_missing(
    task_service, task_list_repo
):
    task_list_id = uuid.uuid4()
    user_id = uuid.uuid4()
    task_list_repo.get_by_id_and_user.return_value = None

    with pytest.raises(NotFoundError):
        await task_service.get_task_list(task_list_id, user_id)


@pytest.mark.asyncio
async def test_create_task_list_creates_with_user_id(task_service, task_list_repo):
    user_id = uuid.uuid4()
    data = TaskListCreate(name="Home", color="#aabbcc", icon="home", position=2)
    created = MagicMock(id=uuid.uuid4(), name="Home", user_id=user_id)
    task_list_repo.create.return_value = created

    result = await task_service.create_task_list(data, user_id)

    assert result == created
    task_list_repo.create.assert_awaited_once_with(
        name="Home",
        color="#AABBCC",
        icon="home",
        position=2,
        user_id=user_id,
    )


@pytest.mark.asyncio
async def test_update_task_list_updates_via_repo(task_service, task_list_repo):
    task_list_id = uuid.uuid4()
    user_id = uuid.uuid4()
    existing = MagicMock(id=task_list_id, user_id=user_id, name="Old")
    updated = MagicMock(id=task_list_id, user_id=user_id, name="New")
    data = TaskListUpdate(name="New")
    task_list_repo.update.return_value = updated

    with patch.object(task_service, "get_task_list", AsyncMock(return_value=existing)):
        result = await task_service.update_task_list(task_list_id, data, user_id)

    assert result == updated
    task_list_repo.update.assert_awaited_once_with(existing, {"name": "New"})


@pytest.mark.asyncio
async def test_delete_task_list_deletes_successfully(task_service, task_list_repo):
    task_list_id = uuid.uuid4()
    user_id = uuid.uuid4()
    task_list_repo.get_by_id_and_user.return_value = MagicMock(
        id=task_list_id,
        user_id=user_id,
    )

    await task_service.delete_task_list(task_list_id, user_id)

    task_list_repo.delete.assert_awaited_once_with(task_list_id)


@pytest.mark.asyncio
async def test_delete_task_list_raises_dependency_conflict_on_integrity_error(
    task_service, task_list_repo
):
    task_list_id = uuid.uuid4()
    user_id = uuid.uuid4()
    task_list_repo.get_by_id_and_user.return_value = MagicMock(
        id=task_list_id,
        user_id=user_id,
    )
    task_list_repo.delete.side_effect = IntegrityError("DELETE", {}, Exception("fk"))

    with pytest.raises(DependencyConflictError):
        await task_service.delete_task_list(task_list_id, user_id)


@pytest.mark.asyncio
async def test_get_tasks_no_filters_returns_user_tasks(task_service, task_repo):
    user_id = uuid.uuid4()
    tasks = [make_task_mock(), make_task_mock()]
    task_repo.get_by_user.return_value = tasks

    result = await task_service.get_tasks(user_id)

    assert result == tasks
    task_repo.get_by_user.assert_awaited_once_with(user_id)


@pytest.mark.asyncio
async def test_get_tasks_with_list_id_filter(task_service, task_repo):
    user_id = uuid.uuid4()
    list_id = uuid.uuid4()
    tasks = [make_task_mock(task_list_id=list_id)]
    task_repo.get_by_user_and_list.return_value = tasks

    result = await task_service.get_tasks(user_id, list_id=list_id)

    assert result == tasks
    task_repo.get_by_user_and_list.assert_awaited_once_with(user_id, list_id)


@pytest.mark.asyncio
async def test_get_tasks_with_status_filter(task_service, task_repo):
    user_id = uuid.uuid4()
    tasks = [make_task_mock(status="done")]
    task_repo.get_by_user_and_status.return_value = tasks

    result = await task_service.get_tasks(user_id, status="done")

    assert result == tasks
    task_repo.get_by_user_and_status.assert_awaited_once_with(user_id, "done")


@pytest.mark.asyncio
async def test_get_tasks_with_list_and_status_filters_in_memory(
    task_service, task_repo
):
    user_id = uuid.uuid4()
    list_id = uuid.uuid4()
    matching = make_task_mock(task_list_id=list_id, status="done")
    wrong_list = make_task_mock(task_list_id=uuid.uuid4(), status="done")
    wrong_status = make_task_mock(task_list_id=list_id, status="todo")
    task_repo.get_by_user.return_value = [matching, wrong_list, wrong_status]

    result = await task_service.get_tasks(user_id, list_id=list_id, status="done")

    assert result == [matching]
    task_repo.get_by_user.assert_awaited_once_with(user_id)


@pytest.mark.asyncio
async def test_get_task_returns_task(task_service, task_repo):
    task_id = uuid.uuid4()
    user_id = uuid.uuid4()
    task = make_task_mock(id=task_id)
    task_repo.get_by_id_and_user.return_value = task

    result = await task_service.get_task(task_id, user_id)

    assert result == task
    task_repo.get_by_id_and_user.assert_awaited_once_with(task_id, user_id)


@pytest.mark.asyncio
async def test_get_task_raises_not_found_when_missing(task_service, task_repo):
    task_id = uuid.uuid4()
    user_id = uuid.uuid4()
    task_repo.get_by_id_and_user.return_value = None

    with pytest.raises(NotFoundError):
        await task_service.get_task(task_id, user_id)


@pytest.mark.asyncio
async def test_create_task_validates_task_list_and_creates(task_service, task_repo):
    user_id = uuid.uuid4()
    task_list_id = uuid.uuid4()
    data = TaskCreate(
        task_list_id=task_list_id,
        title="Write tests",
        description="Cover task service",
        priority="high",
    )
    created = make_task_mock(id=uuid.uuid4(), task_list_id=task_list_id)
    task_repo.create.return_value = created

    with patch.object(task_service, "get_task_list", AsyncMock()) as mock_get_task_list:
        result = await task_service.create_task(data, user_id)

    assert result == created
    mock_get_task_list.assert_awaited_once_with(task_list_id, user_id)
    task_repo.create.assert_awaited_once_with(
        task_list_id=task_list_id,
        category_id=None,
        title="Write tests",
        description="Cover task service",
        priority="high",
        due_date=None,
        scheduled_date=None,
        scheduled_start_time=None,
        scheduled_end_time=None,
        estimated_duration_minutes=None,
        recurrence_rule=None,
        exception_dates=None,
        position=0,
        user_id=user_id,
    )


@pytest.mark.asyncio
async def test_create_task_validates_category_when_provided(
    task_service, activity_service
):
    user_id = uuid.uuid4()
    task_list_id = uuid.uuid4()
    category_id = uuid.uuid4()
    data = TaskCreate(task_list_id=task_list_id, category_id=category_id, title="Task")

    with (
        patch.object(task_service, "get_task_list", AsyncMock()) as mock_get_task_list,
        patch.object(
            task_service.task_repo,
            "create",
            AsyncMock(return_value=make_task_mock()),
        ),
    ):
        await task_service.create_task(data, user_id)

    mock_get_task_list.assert_awaited_once_with(task_list_id, user_id)
    activity_service.get_category.assert_awaited_once_with(category_id, user_id)


@pytest.mark.asyncio
async def test_update_task_validates_category_id_if_provided(
    task_service, task_repo, activity_service
):
    task_id = uuid.uuid4()
    user_id = uuid.uuid4()
    category_id = uuid.uuid4()
    existing = make_task_mock(id=task_id)
    updated = make_task_mock(id=task_id, category_id=category_id)
    data = TaskUpdate(category_id=category_id, title="Updated")
    task_repo.update.return_value = updated

    with patch.object(task_service, "get_task", AsyncMock(return_value=existing)):
        result = await task_service.update_task(task_id, data, user_id)

    assert result == updated
    activity_service.get_category.assert_awaited_once_with(category_id, user_id)
    task_repo.update.assert_awaited_once_with(
        existing,
        {"category_id": category_id, "title": "Updated"},
    )


@pytest.mark.asyncio
async def test_update_task_validates_task_list_if_provided(task_service, task_repo):
    task_id = uuid.uuid4()
    user_id = uuid.uuid4()
    new_task_list_id = uuid.uuid4()
    existing = make_task_mock(id=task_id)
    updated = make_task_mock(id=task_id, task_list_id=new_task_list_id)
    data = TaskUpdate(task_list_id=new_task_list_id)
    task_repo.update.return_value = updated

    with (
        patch.object(task_service, "get_task", AsyncMock(return_value=existing)),
        patch.object(task_service, "get_task_list", AsyncMock()) as mock_get_task_list,
    ):
        result = await task_service.update_task(task_id, data, user_id)

    assert result == updated
    mock_get_task_list.assert_awaited_once_with(new_task_list_id, user_id)
    task_repo.update.assert_awaited_once_with(
        existing,
        {"task_list_id": new_task_list_id},
    )


@pytest.mark.asyncio
async def test_delete_task_deletes_successfully(task_service, task_repo):
    task_id = uuid.uuid4()
    user_id = uuid.uuid4()
    task_repo.get_by_id_and_user.return_value = make_task_mock(id=task_id)

    await task_service.delete_task(task_id, user_id)

    task_repo.delete.assert_awaited_once_with(task_id)


@pytest.mark.asyncio
async def test_delete_task_raises_dependency_conflict_on_integrity_error(
    task_service, task_repo
):
    task_id = uuid.uuid4()
    user_id = uuid.uuid4()
    task_repo.get_by_id_and_user.return_value = make_task_mock(id=task_id)
    task_repo.delete.side_effect = IntegrityError("DELETE", {}, Exception("fk"))

    with pytest.raises(DependencyConflictError):
        await task_service.delete_task(task_id, user_id)


@pytest.mark.asyncio
async def test_generate_occurrences_success(task_service, task_repo):
    task_id = uuid.uuid4()
    user_id = uuid.uuid4()
    task = make_task_mock(
        id=task_id,
        recurrence_rule="FREQ=DAILY",
        scheduled_date=date(2026, 1, 10),
    )
    task_repo.get_by_id_and_user.return_value = task
    task_repo.get_by_user.return_value = []
    task_repo.create.side_effect = [
        make_task_mock(id=uuid.uuid4(), scheduled_date=date(2026, 1, 11)),
        make_task_mock(id=uuid.uuid4(), scheduled_date=date(2026, 1, 12)),
        make_task_mock(id=uuid.uuid4(), scheduled_date=date(2026, 1, 13)),
    ]

    result = await task_service.generate_occurrences(task_id, user_id, count=3)

    assert len(result) == 3
    assert task_repo.create.await_count == 3
    first_call = task_repo.create.await_args_list[0].kwargs
    second_call = task_repo.create.await_args_list[1].kwargs
    assert first_call["scheduled_date"] == date(2026, 1, 11)
    assert second_call["scheduled_date"] == date(2026, 1, 12)


@pytest.mark.asyncio
async def test_generate_occurrences_skips_exception_dates(task_service, task_repo):
    task_id = uuid.uuid4()
    user_id = uuid.uuid4()
    task = make_task_mock(
        id=task_id,
        recurrence_rule="FREQ=DAILY",
        scheduled_date=date(2026, 1, 10),
        exception_dates=["2026-01-11"],
    )
    task_repo.get_by_id_and_user.return_value = task
    task_repo.get_by_user.return_value = []
    task_repo.create.side_effect = [
        make_task_mock(id=uuid.uuid4(), scheduled_date=date(2026, 1, 12)),
        make_task_mock(id=uuid.uuid4(), scheduled_date=date(2026, 1, 13)),
    ]

    result = await task_service.generate_occurrences(task_id, user_id, count=2)

    assert len(result) == 2
    first_call = task_repo.create.await_args_list[0].kwargs
    second_call = task_repo.create.await_args_list[1].kwargs
    assert first_call["scheduled_date"] == date(2026, 1, 12)
    assert second_call["scheduled_date"] == date(2026, 1, 13)


@pytest.mark.asyncio
async def test_generate_occurrences_no_rule(task_service, task_repo):
    task_id = uuid.uuid4()
    user_id = uuid.uuid4()
    task_repo.get_by_id_and_user.return_value = make_task_mock(
        id=task_id,
        recurrence_rule=None,
    )

    with pytest.raises(BadRequestError):
        await task_service.generate_occurrences(task_id, user_id, count=3)

    task_repo.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_generate_rolling_occurrences_creates_only_needed_tasks(
    task_service,
):
    user_id = uuid.uuid4()
    recurring_task = make_task_mock(
        id=uuid.uuid4(),
        title="Daily standup",
        task_list_id=uuid.uuid4(),
        recurrence_rule="FREQ=DAILY",
    )
    existing_future_child = make_task_mock(
        id=uuid.uuid4(),
        title="Daily standup",
        task_list_id=recurring_task.task_list_id,
        status="todo",
        scheduled_date=date.today(),
        recurrence_rule=None,
    )

    with (
        patch.object(
            task_service.task_repo,
            "get_by_user",
            AsyncMock(return_value=[recurring_task, existing_future_child]),
        ) as mock_get_by_user,
        patch.object(
            task_service,
            "generate_occurrences",
            AsyncMock(return_value=[make_task_mock(), make_task_mock()]),
        ) as mock_generate_occurrences,
    ):
        result = await task_service.generate_rolling_occurrences(user_id)

    assert result == {"created_count": 2, "recurring_tasks_checked": 1}
    mock_get_by_user.assert_awaited_once_with(user_id)
    mock_generate_occurrences.assert_awaited_once_with(
        recurring_task.id,
        user_id,
        count=2,
    )


@pytest.mark.asyncio
async def test_complete_task_marks_done_without_tracker(task_service, task_repo):
    task_id = uuid.uuid4()
    user_id = uuid.uuid4()
    task = make_task_mock(id=task_id, status="todo")
    updated = make_task_mock(id=task_id, status="done")
    task_repo.get_by_id_and_user.return_value = task
    task_repo.update.return_value = updated
    data = TaskCompleteRequest(add_to_tracker=False)

    result = await task_service.complete_task(task_id, user_id, data)

    assert result == updated
    task_repo.update.assert_awaited_once_with(task, {"status": "done"})


@pytest.mark.asyncio
async def test_complete_task_with_tracker_creates_activity_and_link(
    task_service, task_repo, task_activity_repo, activity_service
):
    task_id = uuid.uuid4()
    user_id = uuid.uuid4()
    category_id = uuid.uuid4()
    task = make_task_mock(
        id=task_id,
        category_id=category_id,
        scheduled_date=date(2026, 1, 20),
        scheduled_start_time=time(14, 0),
        scheduled_end_time=time(15, 0),
        description="Original notes",
    )
    refreshed = make_task_mock(id=task_id, status="done")
    activity = MagicMock(id=uuid.uuid4())
    task_activity = MagicMock(id=uuid.uuid4(), task_id=task_id, activity_id=activity.id)
    task_repo.get_by_id_and_user.side_effect = [task, refreshed]
    task_repo.update.return_value = make_task_mock(id=task_id, status="done")
    activity_service.create_activity.return_value = activity
    task_activity_repo.create.return_value = task_activity
    data = TaskCompleteRequest(add_to_tracker=True)

    result = await task_service.complete_task(task_id, user_id, data)

    assert result == refreshed
    task_repo.update.assert_awaited_once_with(task, {"status": "done"})
    activity_service.create_activity.assert_awaited_once()
    call_args = activity_service.create_activity.await_args.args
    activity_data = call_args[0]
    assert activity_data.category_id == category_id
    assert activity_data.date == date(2026, 1, 20)
    assert activity_data.start_time == time(14, 0)
    assert activity_data.end_time == time(15, 0)
    assert activity_data.notes == "Original notes"
    assert call_args[1] == user_id
    task_activity_repo.create.assert_awaited_once_with(
        task_id=task_id,
        activity_id=activity.id,
    )


@pytest.mark.asyncio
async def test_complete_task_add_to_tracker_raises_when_category_missing(
    task_service, task_repo
):
    task_id = uuid.uuid4()
    user_id = uuid.uuid4()
    task = make_task_mock(id=task_id, category_id=None)
    task_repo.get_by_id_and_user.return_value = task
    task_repo.update.return_value = make_task_mock(id=task_id, status="done")
    data = TaskCompleteRequest(add_to_tracker=True)

    with pytest.raises(BadRequestError):
        await task_service.complete_task(task_id, user_id, data)


@pytest.mark.asyncio
async def test_complete_task_add_to_tracker_raises_when_date_or_time_missing(
    task_service, task_repo
):
    task_id = uuid.uuid4()
    user_id = uuid.uuid4()
    task = make_task_mock(
        id=task_id,
        category_id=uuid.uuid4(),
        scheduled_date=None,
        scheduled_start_time=time(10, 0),
        scheduled_end_time=time(11, 0),
    )
    task_repo.get_by_id_and_user.return_value = task
    task_repo.update.return_value = make_task_mock(id=task_id, status="done")
    data = TaskCompleteRequest(add_to_tracker=True)

    with pytest.raises(BadRequestError):
        await task_service.complete_task(task_id, user_id, data)


@pytest.mark.asyncio
async def test_convert_task_to_activity_uses_data_category_id_when_provided(
    task_service, task_repo, task_activity_repo, activity_service
):
    task_id = uuid.uuid4()
    user_id = uuid.uuid4()
    provided_category_id = uuid.uuid4()
    task = make_task_mock(id=task_id, category_id=uuid.uuid4(), status="todo")
    activity = MagicMock(id=uuid.uuid4())
    task_activity = MagicMock(id=uuid.uuid4(), task_id=task_id, activity_id=activity.id)
    task_repo.get_by_id_and_user.return_value = task
    activity_service.create_activity.return_value = activity
    task_activity_repo.create.return_value = task_activity
    data = ConvertToActivityRequest(
        date=date(2026, 1, 15),
        start_time=time(9, 0),
        end_time=time(10, 0),
        category_id=provided_category_id,
    )

    result = await task_service.convert_task_to_activity(task_id, user_id, data)

    assert result == task_activity
    activity_service.create_activity.assert_awaited_once()
    activity_data = activity_service.create_activity.await_args.args[0]
    assert activity_data.category_id == provided_category_id
    task_repo.update.assert_awaited_once_with(task, {"status": "done"})


@pytest.mark.asyncio
async def test_convert_task_to_activity_falls_back_to_task_category(
    task_service, task_repo, task_activity_repo, activity_service
):
    task_id = uuid.uuid4()
    user_id = uuid.uuid4()
    task_category_id = uuid.uuid4()
    task = make_task_mock(id=task_id, category_id=task_category_id, status="todo")
    activity = MagicMock(id=uuid.uuid4())
    task_activity = MagicMock(id=uuid.uuid4(), task_id=task_id, activity_id=activity.id)
    task_repo.get_by_id_and_user.return_value = task
    activity_service.create_activity.return_value = activity
    task_activity_repo.create.return_value = task_activity
    data = ConvertToActivityRequest(
        date=date(2026, 1, 15),
        start_time=time(9, 0),
        end_time=time(10, 0),
        notes="Session note",
    )

    result = await task_service.convert_task_to_activity(task_id, user_id, data)

    assert result == task_activity
    activity_data = activity_service.create_activity.await_args.args[0]
    assert activity_data.category_id == task_category_id
    assert activity_data.notes == "Session note"


@pytest.mark.asyncio
async def test_convert_task_to_activity_raises_when_category_missing_everywhere(
    task_service, task_repo, activity_service
):
    task_id = uuid.uuid4()
    user_id = uuid.uuid4()
    task_repo.get_by_id_and_user.return_value = make_task_mock(
        id=task_id,
        category_id=None,
    )
    data = ConvertToActivityRequest(
        date=date(2026, 1, 15),
        start_time=time(9, 0),
        end_time=time(10, 0),
    )

    with pytest.raises(BadRequestError):
        await task_service.convert_task_to_activity(task_id, user_id, data)

    activity_service.create_activity.assert_not_called()


@pytest.mark.asyncio
async def test_convert_task_to_activity_auto_marks_done_when_not_done(
    task_service, task_repo, task_activity_repo, activity_service
):
    task_id = uuid.uuid4()
    user_id = uuid.uuid4()
    task = make_task_mock(id=task_id, status="in_progress")
    task_repo.get_by_id_and_user.return_value = task
    activity_service.create_activity.return_value = MagicMock(id=uuid.uuid4())
    task_activity_repo.create.return_value = MagicMock(id=uuid.uuid4())
    data = ConvertToActivityRequest(
        date=date(2026, 1, 15),
        start_time=time(11, 0),
        end_time=time(12, 0),
        category_id=uuid.uuid4(),
    )

    await task_service.convert_task_to_activity(task_id, user_id, data)

    task_repo.update.assert_awaited_once_with(task, {"status": "done"})


@pytest.mark.asyncio
async def test_convert_task_to_activity_does_not_update_when_already_done(
    task_service, task_repo, task_activity_repo, activity_service
):
    task_id = uuid.uuid4()
    user_id = uuid.uuid4()
    task = make_task_mock(id=task_id, status="done")
    task_repo.get_by_id_and_user.return_value = task
    activity_service.create_activity.return_value = MagicMock(id=uuid.uuid4())
    task_activity_repo.create.return_value = MagicMock(id=uuid.uuid4())
    data = ConvertToActivityRequest(
        date=date(2026, 1, 15),
        start_time=time(11, 0),
        end_time=time(12, 0),
        category_id=uuid.uuid4(),
    )

    await task_service.convert_task_to_activity(task_id, user_id, data)

    task_repo.update.assert_not_awaited()
