from datetime import date, time
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from app.exceptions import DependencyConflictError, NotFoundError
from app.repositories.activity_repository import (
    ActivityRepository,
    CategoryRepository,
    GlobalConstraintsRepository,
    GroupRepository,
)
from app.schemas.activity import (
    ActivityCreate,
    ActivityUpdate,
    CategoryCreate,
    CategoryUpdate,
    GlobalConstraintsUpdate,
    GroupCreate,
    GroupUpdate,
)
from app.services.activity_service import ActivityService


@pytest.fixture
def group_repo():
    return AsyncMock(spec=GroupRepository)


@pytest.fixture
def category_repo():
    return AsyncMock(spec=CategoryRepository)


@pytest.fixture
def constraints_repo():
    return AsyncMock(spec=GlobalConstraintsRepository)


@pytest.fixture
def activity_repo():
    return AsyncMock(spec=ActivityRepository)


@pytest.fixture
def activity_service(group_repo, category_repo, constraints_repo, activity_repo):
    return ActivityService(group_repo, category_repo, constraints_repo, activity_repo)


@pytest.mark.asyncio
async def test_get_groups_returns_groups(activity_service, group_repo):
    user_id = uuid4()
    groups = [MagicMock(id=uuid4(), name="Work", user_id=user_id)]
    group_repo.get_by_user.return_value = groups

    result = await activity_service.get_groups(user_id)

    assert result == groups
    group_repo.get_by_user.assert_awaited_once_with(user_id)


@pytest.mark.asyncio
async def test_get_group_returns_group(activity_service, group_repo):
    group_id = uuid4()
    user_id = uuid4()
    group = MagicMock(id=group_id, name="Health", user_id=user_id)
    group_repo.get_by_id_and_user.return_value = group

    result = await activity_service.get_group(group_id, user_id)

    assert result == group
    group_repo.get_by_id_and_user.assert_awaited_once_with(group_id, user_id)


@pytest.mark.asyncio
async def test_get_group_raises_not_found_when_missing(activity_service, group_repo):
    group_id = uuid4()
    user_id = uuid4()
    group_repo.get_by_id_and_user.return_value = None

    with pytest.raises(NotFoundError):
        await activity_service.get_group(group_id, user_id)


@pytest.mark.asyncio
async def test_create_group_creates_group(activity_service, group_repo):
    user_id = uuid4()
    data = GroupCreate(name="Study", color="#abcdef")
    created = MagicMock(id=uuid4(), name="Study", user_id=user_id)
    group_repo.create.return_value = created

    result = await activity_service.create_group(data, user_id)

    assert result == created
    group_repo.create.assert_awaited_once_with(
        name="Study", color="#ABCDEF", user_id=user_id
    )


@pytest.mark.asyncio
async def test_update_group_updates_group(activity_service, group_repo):
    group_id = uuid4()
    user_id = uuid4()
    existing = MagicMock(id=group_id, name="Old", user_id=user_id)
    updated = MagicMock(id=group_id, name="New", user_id=user_id)
    group_repo.get_by_id_and_user.return_value = existing
    group_repo.update.return_value = updated
    data = GroupUpdate(name="New")

    result = await activity_service.update_group(group_id, data, user_id)

    assert result == updated
    group_repo.update.assert_awaited_once_with(existing, {"name": "New"})


@pytest.mark.asyncio
async def test_delete_group_deletes_group(activity_service, group_repo):
    group_id = uuid4()
    user_id = uuid4()
    group_repo.get_by_id_and_user.return_value = MagicMock(
        id=group_id, name="Group", user_id=user_id
    )

    await activity_service.delete_group(group_id, user_id)

    group_repo.delete.assert_awaited_once_with(group_id)


@pytest.mark.asyncio
async def test_delete_group_raises_dependency_conflict_on_integrity_error(
    activity_service, group_repo
):
    group_id = uuid4()
    user_id = uuid4()
    group_repo.get_by_id_and_user.return_value = MagicMock(
        id=group_id, name="Group", user_id=user_id
    )
    group_repo.delete.side_effect = IntegrityError("DELETE", {}, Exception("fk"))

    with pytest.raises(DependencyConflictError):
        await activity_service.delete_group(group_id, user_id)


@pytest.mark.asyncio
async def test_get_categories_returns_categories(activity_service, category_repo):
    user_id = uuid4()
    categories = [MagicMock(id=uuid4(), name="Reading", user_id=user_id)]
    category_repo.get_by_user.return_value = categories

    result = await activity_service.get_categories(user_id)

    assert result == categories
    category_repo.get_by_user.assert_awaited_once_with(user_id)


@pytest.mark.asyncio
async def test_get_category_returns_category(activity_service, category_repo):
    category_id = uuid4()
    user_id = uuid4()
    category = MagicMock(id=category_id, name="Fitness", user_id=user_id)
    category_repo.get_by_id_and_user.return_value = category

    result = await activity_service.get_category(category_id, user_id)

    assert result == category
    category_repo.get_by_id_and_user.assert_awaited_once_with(category_id, user_id)


@pytest.mark.asyncio
async def test_get_category_raises_not_found_when_missing(
    activity_service, category_repo
):
    category_id = uuid4()
    user_id = uuid4()
    category_repo.get_by_id_and_user.return_value = None

    with pytest.raises(NotFoundError):
        await activity_service.get_category(category_id, user_id)


@pytest.mark.asyncio
async def test_create_category_creates_category(
    activity_service, group_repo, category_repo
):
    user_id = uuid4()
    group_id = uuid4()
    data = CategoryCreate(
        name="Deep Work",
        group_id=group_id,
        priority=2,
        min_weekly_hours=1.0,
        target_weekly_hours=6.0,
        max_weekly_hours=10.0,
        unit="hours",
        mandatory=True,
    )
    group_repo.get_by_id_and_user.return_value = MagicMock(
        id=group_id, name="Work", user_id=user_id
    )
    created = MagicMock(
        id=uuid4(), name="Deep Work", user_id=user_id, group_id=group_id
    )
    category_repo.create.return_value = created

    result = await activity_service.create_category(data, user_id)

    assert result == created
    category_repo.create.assert_awaited_once_with(
        name="Deep Work",
        group_id=group_id,
        priority=2,
        min_weekly_hours=1.0,
        target_weekly_hours=6.0,
        max_weekly_hours=10.0,
        unit="hours",
        mandatory=True,
        user_id=user_id,
    )


@pytest.mark.asyncio
async def test_create_category_raises_when_group_missing(activity_service, group_repo):
    user_id = uuid4()
    group_id = uuid4()
    data = CategoryCreate(name="Deep Work", group_id=group_id)
    group_repo.get_by_id_and_user.return_value = None

    with pytest.raises(NotFoundError):
        await activity_service.create_category(data, user_id)


@pytest.mark.asyncio
async def test_update_category_updates_with_group_check(
    activity_service, category_repo, group_repo
):
    category_id = uuid4()
    group_id = uuid4()
    user_id = uuid4()
    category = MagicMock(id=category_id, name="Old", user_id=user_id)
    updated = MagicMock(
        id=category_id, name="Updated", user_id=user_id, group_id=group_id
    )
    category_repo.get_by_id_and_user.return_value = category
    group_repo.get_by_id_and_user.return_value = MagicMock(
        id=group_id, name="New Group", user_id=user_id
    )
    category_repo.update.return_value = updated
    data = CategoryUpdate(name="Updated", group_id=group_id)

    result = await activity_service.update_category(category_id, data, user_id)

    assert result == updated
    category_repo.update.assert_awaited_once_with(
        category, {"name": "Updated", "group_id": group_id}
    )


@pytest.mark.asyncio
async def test_delete_category_deletes_category(activity_service, category_repo):
    category_id = uuid4()
    user_id = uuid4()
    category_repo.get_by_id_and_user.return_value = MagicMock(
        id=category_id, name="Category", user_id=user_id
    )

    await activity_service.delete_category(category_id, user_id)

    category_repo.delete.assert_awaited_once_with(category_id)


@pytest.mark.asyncio
async def test_get_global_constraints_returns_existing(
    activity_service, constraints_repo
):
    user_id = uuid4()
    constraints = MagicMock(id=uuid4(), user_id=user_id)
    constraints_repo.get_by_user.return_value = constraints

    result = await activity_service.get_global_constraints(user_id)

    assert result == constraints
    constraints_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_get_global_constraints_creates_defaults_when_missing(
    activity_service, constraints_repo
):
    user_id = uuid4()
    created = MagicMock(id=uuid4(), user_id=user_id)
    constraints_repo.get_by_user.return_value = None
    constraints_repo.create.return_value = created

    result = await activity_service.get_global_constraints(user_id)

    assert result == created
    constraints_repo.create.assert_awaited_once_with(user_id=user_id)


@pytest.mark.asyncio
async def test_update_global_constraints_updates_constraints(
    activity_service, constraints_repo
):
    user_id = uuid4()
    constraints = MagicMock(id=uuid4(), user_id=user_id)
    updated = MagicMock(id=constraints.id, user_id=user_id)
    data = GlobalConstraintsUpdate(total_weekly_hours=160.0)
    constraints_repo.update.return_value = updated

    with patch.object(
        activity_service,
        "get_global_constraints",
        AsyncMock(return_value=constraints),
    ) as mock_get_global_constraints:
        result = await activity_service.update_global_constraints(data, user_id)

    assert result == updated
    mock_get_global_constraints.assert_awaited_once_with(user_id)
    constraints_repo.update.assert_awaited_once_with(
        constraints,
        {"total_weekly_hours": 160.0},
    )


@pytest.mark.asyncio
async def test_get_activities_returns_activities(activity_service, activity_repo):
    user_id = uuid4()
    activities = [MagicMock(id=uuid4(), user_id=user_id)]
    activity_repo.get_by_user.return_value = activities

    result = await activity_service.get_activities(user_id)

    assert result == activities
    activity_repo.get_by_user.assert_awaited_once_with(user_id)


@pytest.mark.asyncio
async def test_get_activities_by_date_returns_activities(
    activity_service, activity_repo
):
    user_id = uuid4()
    target_date = date(2026, 1, 5)
    activities = [MagicMock(id=uuid4(), user_id=user_id, date=target_date)]
    activity_repo.get_by_user_and_date.return_value = activities

    result = await activity_service.get_activities_by_date(user_id, target_date)

    assert result == activities
    activity_repo.get_by_user_and_date.assert_awaited_once_with(user_id, target_date)


@pytest.mark.asyncio
async def test_get_activity_returns_activity(activity_service, activity_repo):
    activity_id = uuid4()
    user_id = uuid4()
    activity = MagicMock(id=activity_id, user_id=user_id)
    activity_repo.get_by_id_and_user.return_value = activity

    result = await activity_service.get_activity(activity_id, user_id)

    assert result == activity
    activity_repo.get_by_id_and_user.assert_awaited_once_with(activity_id, user_id)


@pytest.mark.asyncio
async def test_get_activity_raises_not_found_when_missing(
    activity_service, activity_repo
):
    activity_id = uuid4()
    user_id = uuid4()
    activity_repo.get_by_id_and_user.return_value = None

    with pytest.raises(NotFoundError):
        await activity_service.get_activity(activity_id, user_id)


@pytest.mark.asyncio
async def test_create_activity_creates_activity(
    activity_service, category_repo, activity_repo
):
    user_id = uuid4()
    category_id = uuid4()
    data = ActivityCreate(
        date=date(2026, 1, 5),
        start_time=time(9, 0),
        end_time=time(10, 30),
        category_id=category_id,
        notes="Focus block",
    )
    category_repo.get_by_id_and_user.return_value = MagicMock(
        id=category_id, name="Deep Work", user_id=user_id
    )
    created = MagicMock(id=uuid4(), user_id=user_id, category_id=category_id)
    activity_repo.create.return_value = created

    result = await activity_service.create_activity(data, user_id)

    assert result == created
    activity_repo.create.assert_awaited_once_with(
        date=date(2026, 1, 5),
        start_time=time(9, 0),
        end_time=time(10, 30),
        category_id=category_id,
        notes="Focus block",
        user_id=user_id,
    )


@pytest.mark.asyncio
async def test_create_activity_raises_when_category_missing(
    activity_service, category_repo
):
    user_id = uuid4()
    category_id = uuid4()
    data = ActivityCreate(
        date=date(2026, 1, 5),
        start_time=time(9, 0),
        end_time=time(10, 30),
        category_id=category_id,
    )
    category_repo.get_by_id_and_user.return_value = None

    with pytest.raises(NotFoundError):
        await activity_service.create_activity(data, user_id)


@pytest.mark.asyncio
async def test_update_activity_updates_with_category_check(
    activity_service, activity_repo, category_repo
):
    activity_id = uuid4()
    category_id = uuid4()
    user_id = uuid4()
    existing = MagicMock(id=activity_id, user_id=user_id)
    updated = MagicMock(id=activity_id, user_id=user_id, category_id=category_id)
    activity_repo.get_by_id_and_user.return_value = existing
    category_repo.get_by_id_and_user.return_value = MagicMock(
        id=category_id, name="Deep Work", user_id=user_id
    )
    activity_repo.update.return_value = updated
    data = ActivityUpdate(category_id=category_id, notes="Updated notes")

    result = await activity_service.update_activity(activity_id, data, user_id)

    assert result == updated
    activity_repo.update.assert_awaited_once_with(
        existing,
        {"category_id": category_id, "notes": "Updated notes"},
    )


@pytest.mark.asyncio
async def test_delete_activity_deletes_activity(activity_service, activity_repo):
    activity_id = uuid4()
    user_id = uuid4()
    activity_repo.get_by_id_and_user.return_value = MagicMock(
        id=activity_id, user_id=user_id
    )

    await activity_service.delete_activity(activity_id, user_id)

    activity_repo.delete.assert_awaited_once_with(activity_id)
