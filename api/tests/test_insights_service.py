from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.services.insights_service import InsightsService


@pytest.fixture
def user_id():
    return uuid4()


@pytest.fixture
def target_date():
    return date(2026, 1, 14)


def _build_daily_repo_mock() -> MagicMock:
    repo = MagicMock()
    repo.get_day_total_minutes = AsyncMock(side_effect=[180.0, 120.0])
    repo.get_day_group_breakdown = AsyncMock(
        side_effect=[
            [
                {
                    "group_id": "g1",
                    "group_name": "Work",
                    "color": "#123456",
                    "minutes": 120.0,
                },
                {
                    "group_id": "g2",
                    "group_name": "Life",
                    "color": None,
                    "minutes": 60.0,
                },
            ],
            [
                {
                    "group_id": "g1",
                    "group_name": "Work",
                    "color": "#123456",
                    "minutes": 90.0,
                }
            ],
        ]
    )
    repo.get_day_top_categories = AsyncMock(
        side_effect=[
            [
                {
                    "category_id": "c1",
                    "category_name": "Coding",
                    "group_name": "Work",
                    "group_color": "#123456",
                    "minutes": 100.0,
                }
            ],
            [
                {
                    "category_id": "c1",
                    "category_name": "Coding",
                    "group_name": "Work",
                    "group_color": "#123456",
                    "minutes": 80.0,
                }
            ],
        ]
    )
    repo.get_day_activities_stats = AsyncMock(
        side_effect=[
            {"activities_count": 4, "unique_categories": 2, "average_duration": 45.0},
            {"activities_count": 3, "unique_categories": 1, "average_duration": 40.0},
        ]
    )
    repo.get_day_longest_activity = AsyncMock(
        return_value={
            "category_name": "Coding",
            "minutes": 75.0,
            "date": date(2026, 1, 14),
            "start_time": "09:00",
            "end_time": "10:15",
        }
    )
    repo.get_day_mandatory_minutes = AsyncMock(side_effect=[120.0, 90.0])
    return repo


def _build_weekly_repo_mock(week_date: date) -> MagicMock:
    current_week_start = week_date - timedelta(days=week_date.weekday())
    current_week_end = current_week_start + timedelta(days=6)
    previous_week_start = current_week_start - timedelta(days=7)
    previous_week_end = current_week_end - timedelta(days=7)

    repo = MagicMock()
    repo._get_week_bounds = MagicMock(
        side_effect=[
            (current_week_start, current_week_end),
            (previous_week_start, previous_week_end),
        ]
    )
    repo.get_week_total_minutes = AsyncMock(side_effect=[700.0, 560.0])
    repo.get_week_group_breakdown = AsyncMock(
        side_effect=[
            [
                {
                    "group_id": "g1",
                    "group_name": "Work",
                    "color": "#123456",
                    "minutes": 500.0,
                }
            ],
            [
                {
                    "group_id": "g1",
                    "group_name": "Work",
                    "color": "#123456",
                    "minutes": 400.0,
                }
            ],
        ]
    )
    repo.get_week_top_categories = AsyncMock(
        side_effect=[
            [
                {
                    "category_id": "c1",
                    "category_name": "Coding",
                    "group_name": "Work",
                    "group_color": "#123456",
                    "minutes": 450.0,
                }
            ],
            [
                {
                    "category_id": "c1",
                    "category_name": "Coding",
                    "group_name": "Work",
                    "group_color": "#123456",
                    "minutes": 360.0,
                }
            ],
        ]
    )
    repo.get_week_activities_stats = AsyncMock(
        side_effect=[
            {"activities_count": 12, "unique_categories": 4, "average_duration": 58.0},
            {"activities_count": 10, "unique_categories": 3, "average_duration": 56.0},
        ]
    )
    repo.get_week_daily_breakdown = AsyncMock(
        return_value=[
            {
                "date": current_week_start,
                "day_name": "Monday",
                "minutes": 120.0,
                "activities_count": 2,
            },
            {
                "date": current_week_start + timedelta(days=1),
                "day_name": "Tuesday",
                "minutes": 100.0,
                "activities_count": 2,
            },
        ]
    )
    repo.get_week_most_productive_day = AsyncMock(
        return_value={
            "date": current_week_start + timedelta(days=2),
            "day_name": "Wednesday",
            "minutes": 150.0,
        }
    )
    repo.get_week_least_productive_day = AsyncMock(
        return_value={
            "date": current_week_start + timedelta(days=6),
            "day_name": "Sunday",
            "minutes": 40.0,
        }
    )
    repo.get_week_longest_activity = AsyncMock(
        return_value={
            "category_name": "Coding",
            "minutes": 120.0,
            "date": current_week_start + timedelta(days=3),
        }
    )
    repo.get_week_goals_progress = AsyncMock(
        return_value=[
            {
                "category_id": "c1",
                "category_name": "Coding",
                "current_week_minutes": 450,
                "min_weekly_minutes": 240,
                "target_weekly_minutes": 420,
                "max_weekly_minutes": 600,
                "progress_percent": 107.14,
                "status": "target_met",
            }
        ]
    )
    return repo


def test_calculate_percent_change_previous_zero_current_positive():
    result = InsightsService._calculate_percent_change(10.0, 0.0)
    assert result == 100.0


def test_calculate_percent_change_previous_zero_current_zero():
    result = InsightsService._calculate_percent_change(0.0, 0.0)
    assert result == 0.0


def test_calculate_percent_change_normal_calculation():
    result = InsightsService._calculate_percent_change(120.0, 80.0)
    assert result == 50.0


def test_calculate_percent_change_negative_change():
    result = InsightsService._calculate_percent_change(30.0, 60.0)
    assert result == -50.0


@pytest.mark.asyncio
async def test_get_daily_comparison_returns_expected_structure(user_id, target_date):
    repo = _build_daily_repo_mock()
    service = InsightsService(repo)

    result = await service.get_daily_comparison(user_id, target_date)

    assert set(result.keys()) == {
        "date",
        "previous_date",
        "total_minutes",
        "previous_total_minutes",
        "total_minutes_delta",
        "total_minutes_percent_change",
        "group_breakdown",
        "top_categories",
        "stats",
        "productivity",
    }
    assert result["date"] == target_date.isoformat()
    assert result["previous_date"] == (target_date - timedelta(days=1)).isoformat()
    assert set(result["stats"].keys()) == {
        "activities_count",
        "previous_activities_count",
        "activities_count_delta",
        "categories_used",
        "previous_categories_used",
        "categories_used_delta",
        "average_activity_duration",
        "previous_average_activity_duration",
        "average_activity_duration_delta",
        "longest_activity",
    }
    assert result["group_breakdown"][0]["group_name"] == "Work"
    assert result["top_categories"][0]["category_name"] == "Coding"


@pytest.mark.asyncio
async def test_get_daily_comparison_awaits_all_repo_methods(user_id, target_date):
    repo = _build_daily_repo_mock()
    service = InsightsService(repo)

    await service.get_daily_comparison(user_id, target_date)

    previous_date = target_date - timedelta(days=1)
    repo.get_day_total_minutes.assert_any_await(user_id, target_date)
    repo.get_day_total_minutes.assert_any_await(user_id, previous_date)
    repo.get_day_group_breakdown.assert_any_await(user_id, target_date)
    repo.get_day_group_breakdown.assert_any_await(user_id, previous_date)
    repo.get_day_top_categories.assert_any_await(user_id, target_date)
    repo.get_day_top_categories.assert_any_await(user_id, previous_date)
    repo.get_day_activities_stats.assert_any_await(user_id, target_date)
    repo.get_day_activities_stats.assert_any_await(user_id, previous_date)
    repo.get_day_longest_activity.assert_awaited_once_with(user_id, target_date)
    repo.get_day_mandatory_minutes.assert_any_await(user_id, target_date)
    repo.get_day_mandatory_minutes.assert_any_await(user_id, previous_date)


@pytest.mark.asyncio
async def test_get_daily_comparison_no_data_returns_zeroes(user_id, target_date):
    repo = MagicMock()
    repo.get_day_total_minutes = AsyncMock(side_effect=[0.0, 0.0])
    repo.get_day_group_breakdown = AsyncMock(side_effect=[[], []])
    repo.get_day_top_categories = AsyncMock(side_effect=[[], []])
    repo.get_day_activities_stats = AsyncMock(
        side_effect=[
            {"activities_count": 0, "unique_categories": 0, "average_duration": 0.0},
            {"activities_count": 0, "unique_categories": 0, "average_duration": 0.0},
        ]
    )
    repo.get_day_longest_activity = AsyncMock(return_value=None)
    repo.get_day_mandatory_minutes = AsyncMock(side_effect=[0.0, 0.0])
    service = InsightsService(repo)

    result = await service.get_daily_comparison(user_id, target_date)

    assert result["total_minutes"] == 0
    assert result["previous_total_minutes"] == 0
    assert result["total_minutes_percent_change"] == 0.0
    assert result["group_breakdown"] == []
    assert result["top_categories"] == []
    assert result["productivity"] is None
    assert result["stats"]["longest_activity"] is None


@pytest.mark.asyncio
async def test_get_daily_comparison_productivity_values(user_id, target_date):
    repo = _build_daily_repo_mock()
    service = InsightsService(repo)

    result = await service.get_daily_comparison(user_id, target_date)

    assert result["productivity"]["mandatory_minutes"] == 120
    assert result["productivity"]["optional_minutes"] == 60
    assert result["productivity"]["mandatory_minutes_delta"] == 30
    assert result["productivity"]["optional_minutes_delta"] == 30


@pytest.mark.asyncio
async def test_get_weekly_comparison_returns_expected_structure(user_id, target_date):
    repo = _build_weekly_repo_mock(target_date)
    service = InsightsService(repo)

    result = await service.get_weekly_comparison(user_id, target_date)

    assert set(result.keys()) == {
        "week_start_date",
        "week_end_date",
        "previous_week_start_date",
        "previous_week_end_date",
        "total_minutes",
        "previous_total_minutes",
        "total_minutes_delta",
        "total_minutes_percent_change",
        "group_breakdown",
        "top_categories",
        "stats",
        "daily_breakdown",
        "goals_progress",
    }
    assert set(result["stats"].keys()) == {
        "activities_count",
        "previous_activities_count",
        "activities_count_delta",
        "categories_used",
        "previous_categories_used",
        "categories_used_delta",
        "average_activity_duration",
        "previous_average_activity_duration",
        "average_activity_duration_delta",
        "average_daily_minutes",
        "previous_average_daily_minutes",
        "average_daily_minutes_delta",
        "most_productive_day",
        "least_productive_day",
        "longest_activity",
    }
    assert result["group_breakdown"][0]["group_name"] == "Work"
    assert result["top_categories"][0]["category_name"] == "Coding"


@pytest.mark.asyncio
async def test_get_weekly_comparison_awaits_all_repo_methods(user_id, target_date):
    repo = _build_weekly_repo_mock(target_date)
    service = InsightsService(repo)

    await service.get_weekly_comparison(user_id, target_date)

    current_week_start = target_date - timedelta(days=target_date.weekday())
    current_week_end = current_week_start + timedelta(days=6)
    previous_week_start = current_week_start - timedelta(days=7)
    previous_week_end = current_week_end - timedelta(days=7)

    repo._get_week_bounds.assert_any_call(target_date)
    repo._get_week_bounds.assert_any_call(current_week_start - timedelta(days=7))
    repo.get_week_total_minutes.assert_any_await(
        user_id, current_week_start, current_week_end
    )
    repo.get_week_total_minutes.assert_any_await(
        user_id, previous_week_start, previous_week_end
    )
    repo.get_week_group_breakdown.assert_any_await(
        user_id, current_week_start, current_week_end
    )
    repo.get_week_group_breakdown.assert_any_await(
        user_id, previous_week_start, previous_week_end
    )
    repo.get_week_top_categories.assert_any_await(
        user_id, current_week_start, current_week_end
    )
    repo.get_week_top_categories.assert_any_await(
        user_id, previous_week_start, previous_week_end
    )
    repo.get_week_activities_stats.assert_any_await(
        user_id, current_week_start, current_week_end
    )
    repo.get_week_activities_stats.assert_any_await(
        user_id, previous_week_start, previous_week_end
    )
    repo.get_week_daily_breakdown.assert_awaited_once_with(
        user_id, current_week_start, current_week_end
    )
    repo.get_week_most_productive_day.assert_awaited_once_with(
        user_id, current_week_start, current_week_end
    )
    repo.get_week_least_productive_day.assert_awaited_once_with(
        user_id, current_week_start, current_week_end
    )
    repo.get_week_longest_activity.assert_awaited_once_with(
        user_id, current_week_start, current_week_end
    )
    repo.get_week_goals_progress.assert_awaited_once_with(
        user_id, current_week_start, current_week_end
    )


@pytest.mark.asyncio
async def test_get_weekly_comparison_no_data_returns_zeroes(user_id, target_date):
    current_week_start = target_date - timedelta(days=target_date.weekday())
    current_week_end = current_week_start + timedelta(days=6)
    previous_week_start = current_week_start - timedelta(days=7)
    previous_week_end = current_week_end - timedelta(days=7)

    repo = MagicMock()
    repo._get_week_bounds = MagicMock(
        side_effect=[
            (current_week_start, current_week_end),
            (previous_week_start, previous_week_end),
        ]
    )
    repo.get_week_total_minutes = AsyncMock(side_effect=[0.0, 0.0])
    repo.get_week_group_breakdown = AsyncMock(side_effect=[[], []])
    repo.get_week_top_categories = AsyncMock(side_effect=[[], []])
    repo.get_week_activities_stats = AsyncMock(
        side_effect=[
            {"activities_count": 0, "unique_categories": 0, "average_duration": 0.0},
            {"activities_count": 0, "unique_categories": 0, "average_duration": 0.0},
        ]
    )
    repo.get_week_daily_breakdown = AsyncMock(return_value=[])
    repo.get_week_most_productive_day = AsyncMock(return_value=None)
    repo.get_week_least_productive_day = AsyncMock(return_value=None)
    repo.get_week_longest_activity = AsyncMock(return_value=None)
    repo.get_week_goals_progress = AsyncMock(return_value=None)
    service = InsightsService(repo)

    result = await service.get_weekly_comparison(user_id, target_date)

    assert result["total_minutes"] == 0
    assert result["previous_total_minutes"] == 0
    assert result["total_minutes_percent_change"] == 0.0
    assert result["group_breakdown"] == []
    assert result["top_categories"] == []
    assert result["daily_breakdown"] == []
    assert result["goals_progress"] is None
    assert result["stats"]["most_productive_day"] is None
    assert result["stats"]["least_productive_day"] is None
    assert result["stats"]["longest_activity"] is None


@pytest.mark.asyncio
async def test_get_weekly_comparison_handles_none_most_productive_day(
    user_id, target_date
):
    repo = _build_weekly_repo_mock(target_date)
    repo.get_week_most_productive_day = AsyncMock(return_value=None)
    service = InsightsService(repo)

    result = await service.get_weekly_comparison(user_id, target_date)

    assert result["stats"]["most_productive_day"] is None
    assert result["stats"]["least_productive_day"] is not None
