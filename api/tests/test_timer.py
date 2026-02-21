from datetime import date, datetime, time
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

import app.models.refresh_token  # noqa: F401
from app.api.v1.endpoints.timer import (
    TimerStartRequest,
    TimerStopAtRequest,
    get_active_timer,
    start_timer,
    stop_timer,
    stop_timer_at,
)
from app.exceptions import ConflictError, NotFoundError
from app.models.activity import Activity, Category
from app.schemas.activity import ActivityResponse


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.execute = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    return db


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = uuid4()
    return user


def mock_query_result(value):
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    return result


def make_activity(
    user_id,
    *,
    category_id=None,
    end_time_value=None,
):
    activity = Activity(
        user_id=user_id,
        category_id=category_id or uuid4(),
        date=date(2026, 1, 5),
        start_time=time(0, 0),
        end_time=end_time_value,
    )
    activity.id = uuid4()
    activity.created_at = datetime(2026, 1, 5, 9, 0)
    activity.updated_at = datetime(2026, 1, 5, 9, 0)
    return activity


def make_category(user_id, category_id):
    category = Category(
        id=category_id,
        user_id=user_id,
        group_id=uuid4(),
        name="Focus",
    )
    category.created_at = datetime(2026, 1, 5, 9, 0)
    category.updated_at = datetime(2026, 1, 5, 9, 0)
    return category


@pytest.mark.asyncio
async def test_start_timer_creates_activity(mock_db, mock_user):
    category_id = uuid4()
    data = TimerStartRequest(category_id=category_id)
    category = make_category(mock_user.id, category_id)
    mock_db.execute.side_effect = [
        mock_query_result(None),
        mock_query_result(category),
    ]

    async def refresh_side_effect(activity):
        activity.id = uuid4()
        activity.created_at = datetime(2026, 1, 5, 9, 0)
        activity.updated_at = datetime(2026, 1, 5, 9, 0)

    mock_db.refresh.side_effect = refresh_side_effect

    result = await start_timer(data, mock_user, mock_db)

    assert isinstance(result, ActivityResponse)
    mock_db.add.assert_called_once()
    mock_db.commit.assert_awaited_once()
    mock_db.refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_start_timer_raises_conflict_when_already_running(mock_db, mock_user):
    active_timer = make_activity(mock_user.id, end_time_value=None)
    mock_db.execute.return_value = mock_query_result(active_timer)
    data = TimerStartRequest(category_id=uuid4())

    with pytest.raises(ConflictError):
        await start_timer(data, mock_user, mock_db)


@pytest.mark.asyncio
async def test_start_timer_raises_not_found_for_invalid_category(mock_db, mock_user):
    data = TimerStartRequest(category_id=uuid4())
    mock_db.execute.side_effect = [
        mock_query_result(None),
        mock_query_result(None),
    ]

    with pytest.raises(NotFoundError):
        await start_timer(data, mock_user, mock_db)


@pytest.mark.asyncio
async def test_stop_timer_sets_end_time(mock_db, mock_user):
    activity = make_activity(mock_user.id, end_time_value=None)
    mock_db.execute.return_value = mock_query_result(activity)

    result = await stop_timer(mock_user, mock_db)

    assert activity.end_time is not None
    assert isinstance(result, ActivityResponse)
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_stop_timer_raises_not_found_when_no_active(mock_db, mock_user):
    mock_db.execute.return_value = mock_query_result(None)

    with pytest.raises(NotFoundError):
        await stop_timer(mock_user, mock_db)


@pytest.mark.asyncio
async def test_stop_timer_at_sets_specific_end_time(mock_db, mock_user):
    activity = make_activity(mock_user.id, end_time_value=None)
    mock_db.execute.return_value = mock_query_result(activity)
    specific_time = time(10, 30)

    result = await stop_timer_at(
        TimerStopAtRequest(end_time=specific_time),
        mock_user,
        mock_db,
    )

    assert activity.end_time == specific_time
    assert result.end_time == specific_time
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_stop_timer_at_raises_not_found(mock_db, mock_user):
    mock_db.execute.return_value = mock_query_result(None)

    with pytest.raises(NotFoundError):
        await stop_timer_at(
            TimerStopAtRequest(end_time=time(10, 30)),
            mock_user,
            mock_db,
        )


@pytest.mark.asyncio
async def test_get_active_timer_returns_activity(mock_db, mock_user):
    activity = make_activity(mock_user.id, end_time_value=None)
    mock_db.execute.return_value = mock_query_result(activity)

    result = await get_active_timer(mock_user, mock_db)

    assert isinstance(result, ActivityResponse)
    assert result.id == activity.id


@pytest.mark.asyncio
async def test_get_active_timer_raises_not_found_when_none(mock_db, mock_user):
    mock_db.execute.return_value = mock_query_result(None)

    with pytest.raises(NotFoundError):
        await get_active_timer(mock_user, mock_db)


@pytest.mark.asyncio
async def test_full_flow_start_then_stop(mock_db, mock_user):
    category_id = uuid4()
    category = make_category(mock_user.id, category_id)
    captured_activity: dict[str, Activity | None] = {"activity": None}

    def add_side_effect(activity: Activity) -> None:
        captured_activity["activity"] = activity

    mock_db.add.side_effect = add_side_effect

    async def execute_side_effect(*_args, **_kwargs):
        call_count = mock_db.execute.await_count
        if call_count == 1:
            return mock_query_result(None)
        if call_count == 2:
            return mock_query_result(category)
        return mock_query_result(captured_activity["activity"])

    async def refresh_side_effect(activity: Activity) -> None:
        if activity.id is None:
            activity.id = uuid4()
            activity.created_at = datetime(2026, 1, 5, 9, 0)
        activity.updated_at = datetime(2026, 1, 5, 9, 0)

    mock_db.execute.side_effect = execute_side_effect
    mock_db.refresh.side_effect = refresh_side_effect

    start_result = await start_timer(
        TimerStartRequest(category_id=category_id),
        mock_user,
        mock_db,
    )
    assert captured_activity["activity"] is not None
    captured_activity["activity"].start_time = time(0, 0)
    stop_result = await stop_timer(mock_user, mock_db)

    assert isinstance(start_result, ActivityResponse)
    assert isinstance(stop_result, ActivityResponse)
    assert start_result.category_id == category_id
    assert start_result.id == stop_result.id
    assert stop_result.end_time is not None
    assert mock_db.commit.await_count == 2


def test_timer_stop_at_request_validates_time():
    req = TimerStopAtRequest.model_validate({"end_time": "10:30"})
    assert req.end_time == time(10, 30)

    with pytest.raises(ValueError):
        TimerStopAtRequest.model_validate({"end_time": "25:00"})


@pytest.mark.asyncio
async def test_stop_timer_midnight_spanning(mock_db, mock_user):
    category_id = uuid4()
    activity = Activity(
        id=uuid4(),
        user_id=mock_user.id,
        category_id=category_id,
        date=date(2026, 2, 21),
        start_time=time(23, 0),
        end_time=None,
    )
    mock_db.execute.return_value = mock_query_result(activity)

    async def refresh_side_effect(activity_to_refresh: Activity) -> None:
        activity_to_refresh.created_at = datetime(2026, 2, 21, 23, 0)
        activity_to_refresh.updated_at = datetime(2026, 2, 22, 0, 30)

    mock_db.refresh.side_effect = refresh_side_effect

    result = await stop_timer_at(
        TimerStopAtRequest(end_time=time(0, 30)),
        mock_user,
        mock_db,
    )

    assert activity.end_time == time(0, 30)
    assert result.end_time == time(0, 30)
    mock_db.commit.assert_awaited_once()


def test_response_model_allows_midnight_spanning():
    response = ActivityResponse(
        id=uuid4(),
        date=date(2026, 2, 21),
        start_time=time(23, 0),
        end_time=time(0, 30),
        category_id=uuid4(),
        notes=None,
        created_at=datetime(2026, 2, 21, 23, 0),
        updated_at=datetime(2026, 2, 21, 23, 0),
    )
    assert response.end_time == time(0, 30)
    assert response.start_time == time(23, 0)


def test_create_activity_still_validates_end_after_start():
    from app.schemas.activity import ActivityCreate

    with pytest.raises(ValueError, match="end_time must be after start_time"):
        ActivityCreate(
            date=date(2026, 2, 21),
            start_time=time(10, 0),
            end_time=time(9, 0),
            category_id=uuid4(),
        )
