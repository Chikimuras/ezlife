from datetime import datetime
from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch
from uuid import uuid4

import pytest

import app.models.refresh_token  # noqa: F401
import app.models.user  # noqa: F401
from app.models.activity import Activity, Category, Group
from app.services.import_service import ImportService


def _make_execute_result(*, first=None, all_items=None):
    result = MagicMock()
    scalars = MagicMock()
    scalars.first.return_value = first
    scalars.all.return_value = all_items or []
    result.scalars.return_value = scalars
    return result


def _make_workbook(sheet_names, sheets):
    workbook = MagicMock()
    type(workbook).sheetnames = PropertyMock(return_value=sheet_names)
    workbook.__getitem__.side_effect = lambda name: sheets[name]
    return workbook


def _make_row(
    date_value,
    start_hour,
    start_minute,
    end_hour,
    end_minute,
    category_name,
    notes=None,
):
    return (
        date_value,
        None,
        start_hour,
        start_minute,
        end_hour,
        end_minute,
        None,
        None,
        None,
        category_name,
        None,
        notes,
    )


@pytest.fixture
def user_id():
    return uuid4()


@pytest.fixture
def session():
    mock_session = MagicMock()
    mock_session.execute = AsyncMock()
    mock_session.flush = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.add = MagicMock()
    return mock_session


@pytest.fixture
def service(session):
    return ImportService(session)


@pytest.mark.asyncio
async def test_import_excel_success_with_parametre_and_journal_sheets(
    service, session, user_id
):
    parametre_sheet = MagicMock()
    parametre_sheet.iter_rows.return_value = [
        ("Deep Work", "Work", 2, 1.0, 5.0, 10.0, "hours", "oui")
    ]

    journal_sheet = MagicMock()
    journal_sheet.iter_rows.return_value = [
        _make_row(datetime(2026, 1, 15, 0, 0), 9, 0, 10, 30, "Deep Work", "Focus")
    ]

    category_for_lookup = MagicMock()
    category_for_lookup.id = uuid4()
    category_for_lookup.name = "Deep Work"

    workbook = _make_workbook(
        ["Paramètre", "Journal"],
        {"Paramètre": parametre_sheet, "Journal": journal_sheet},
    )

    session.execute.side_effect = [
        _make_execute_result(first=None),
        _make_execute_result(all_items=[category_for_lookup]),
    ]

    with patch("app.services.import_service.load_workbook", return_value=workbook):
        result = await service.import_excel(BytesIO(b"dummy"), user_id)

    assert result["groups_created"] == 1
    assert result["categories_created"] == 1
    assert result["activities_created"] == 1
    assert result["errors"] == []
    assert session.flush.await_count == 1
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_import_excel_returns_error_when_workbook_load_fails(service, user_id):
    with patch(
        "app.services.import_service.load_workbook",
        side_effect=Exception("bad excel"),
    ):
        result = await service.import_excel(BytesIO(b"dummy"), user_id)

    assert result["groups_created"] == 0
    assert result["categories_created"] == 0
    assert result["activities_created"] == 0
    assert result["errors"] == ["Failed to load Excel file: bad excel"]


@pytest.mark.asyncio
async def test_parametre_sheet_creates_groups_and_categories(service, session, user_id):
    parametre_sheet = MagicMock()
    parametre_sheet.iter_rows.return_value = [
        ("Coding", "Work", 1, 0.0, 5.0, 8.0, "hours", "oui"),
        ("Running", "Health", 3, 1.0, 2.0, 4.0, "minutes", "non"),
    ]
    workbook = _make_workbook(["Paramètre"], {"Paramètre": parametre_sheet})

    session.execute.side_effect = [
        _make_execute_result(first=None),
        _make_execute_result(first=None),
    ]

    with patch("app.services.import_service.load_workbook", return_value=workbook):
        result = await service.import_excel(BytesIO(b"dummy"), user_id)

    assert result["groups_created"] == 2
    assert result["categories_created"] == 2
    assert result["activities_created"] == 0
    assert result["errors"] == []

    added_objects = [call.args[0] for call in session.add.call_args_list]
    added_groups = [obj for obj in added_objects if isinstance(obj, Group)]
    added_categories = [obj for obj in added_objects if isinstance(obj, Category)]
    assert len(added_groups) == 2
    assert len(added_categories) == 2


@pytest.mark.asyncio
async def test_parametre_sheet_reuses_existing_group(service, session, user_id):
    parametre_sheet = MagicMock()
    parametre_sheet.iter_rows.return_value = [
        ("Reading", "Learning", 1, 0.0, 2.0, 4.0, "hours", "non")
    ]
    workbook = _make_workbook(["Paramètre"], {"Paramètre": parametre_sheet})

    existing_group = MagicMock(spec=Group)
    existing_group.id = uuid4()

    session.execute.return_value = _make_execute_result(first=existing_group)

    with patch("app.services.import_service.load_workbook", return_value=workbook):
        result = await service.import_excel(BytesIO(b"dummy"), user_id)

    assert result["groups_created"] == 0
    assert result["categories_created"] == 1
    assert result["errors"] == []

    added_objects = [call.args[0] for call in session.add.call_args_list]
    assert not any(isinstance(obj, Group) for obj in added_objects)
    assert any(isinstance(obj, Category) for obj in added_objects)


@pytest.mark.asyncio
async def test_parametre_sheet_row_error_is_collected_and_processing_continues(
    service, session, user_id
):
    parametre_sheet = MagicMock()
    parametre_sheet.iter_rows.return_value = [
        ("Bad Row", "Work", "NaN", 0.0, 1.0, 2.0, "hours", "non"),
        ("Good Row", "Work", 1, 0.0, 2.0, 3.0, "hours", "oui"),
    ]
    workbook = _make_workbook(["Paramètre"], {"Paramètre": parametre_sheet})

    session.execute.return_value = _make_execute_result(first=None)

    with patch("app.services.import_service.load_workbook", return_value=workbook):
        result = await service.import_excel(BytesIO(b"dummy"), user_id)

    assert result["groups_created"] == 1
    assert result["categories_created"] == 1
    assert len(result["errors"]) == 1
    assert "Row 2 in Paramètre" in result["errors"][0]


@pytest.mark.asyncio
async def test_journal_sheet_creates_valid_activities(service, session, user_id):
    journal_sheet = MagicMock()
    journal_sheet.iter_rows.return_value = [
        _make_row(datetime(2026, 1, 16, 0, 0), 8, 15, 9, 45, "Workout", "Leg day")
    ]
    workbook = _make_workbook(["Journal"], {"Journal": journal_sheet})

    category = MagicMock(spec=Category)
    category.id = uuid4()
    category.name = "Workout"
    session.execute.return_value = _make_execute_result(all_items=[category])

    with patch("app.services.import_service.load_workbook", return_value=workbook):
        result = await service.import_excel(BytesIO(b"dummy"), user_id)

    assert result["groups_created"] == 0
    assert result["categories_created"] == 0
    assert result["activities_created"] == 1
    assert result["errors"] == []

    added_objects = [call.args[0] for call in session.add.call_args_list]
    added_activities = [obj for obj in added_objects if isinstance(obj, Activity)]
    assert len(added_activities) == 1
    assert added_activities[0].notes == "Leg day"


@pytest.mark.asyncio
async def test_journal_sheet_invalid_date_adds_error(service, session, user_id):
    journal_sheet = MagicMock()
    journal_sheet.iter_rows.return_value = [
        _make_row("2026-01-17", 9, 0, 10, 0, "Deep Work")
    ]
    workbook = _make_workbook(["Journal"], {"Journal": journal_sheet})

    session.execute.return_value = _make_execute_result(all_items=[])

    with patch("app.services.import_service.load_workbook", return_value=workbook):
        result = await service.import_excel(BytesIO(b"dummy"), user_id)

    assert result["activities_created"] == 0
    assert "Row 2 in Journal: Invalid date format" in result["errors"]


@pytest.mark.asyncio
async def test_journal_sheet_missing_time_values_adds_error(service, session, user_id):
    journal_sheet = MagicMock()
    journal_sheet.iter_rows.return_value = [
        _make_row(datetime(2026, 1, 18, 0, 0), 9, None, 10, 0, "Deep Work")
    ]
    workbook = _make_workbook(["Journal"], {"Journal": journal_sheet})

    session.execute.return_value = _make_execute_result(all_items=[])

    with patch("app.services.import_service.load_workbook", return_value=workbook):
        result = await service.import_excel(BytesIO(b"dummy"), user_id)

    assert result["activities_created"] == 0
    assert "Row 2 in Journal: Missing time values" in result["errors"]


@pytest.mark.asyncio
async def test_journal_sheet_end_time_before_start_time_adds_error(
    service, session, user_id
):
    journal_sheet = MagicMock()
    journal_sheet.iter_rows.return_value = [
        _make_row(datetime(2026, 1, 19, 0, 0), 11, 0, 10, 30, "Deep Work")
    ]
    workbook = _make_workbook(["Journal"], {"Journal": journal_sheet})

    session.execute.return_value = _make_execute_result(all_items=[])

    with patch("app.services.import_service.load_workbook", return_value=workbook):
        result = await service.import_excel(BytesIO(b"dummy"), user_id)

    assert result["activities_created"] == 0
    assert "Row 2 in Journal: End time must be after start time" in result["errors"]


@pytest.mark.asyncio
async def test_journal_sheet_unknown_category_adds_error(service, session, user_id):
    journal_sheet = MagicMock()
    journal_sheet.iter_rows.return_value = [
        _make_row(datetime(2026, 1, 20, 0, 0), 9, 0, 10, 0, "Unknown")
    ]
    workbook = _make_workbook(["Journal"], {"Journal": journal_sheet})

    known_category = MagicMock(spec=Category)
    known_category.id = uuid4()
    known_category.name = "Known"
    session.execute.return_value = _make_execute_result(all_items=[known_category])

    with patch("app.services.import_service.load_workbook", return_value=workbook):
        result = await service.import_excel(BytesIO(b"dummy"), user_id)

    assert result["activities_created"] == 0
    assert "Row 2 in Journal: Category 'Unknown' not found" in result["errors"]


@pytest.mark.asyncio
async def test_database_commit_failure_rolls_back_and_returns_error(
    service, session, user_id
):
    parametre_sheet = MagicMock()
    parametre_sheet.iter_rows.return_value = [
        ("Coding", "Work", 1, 0.0, 1.0, 2.0, "hours", "oui")
    ]
    workbook = _make_workbook(["Paramètre"], {"Paramètre": parametre_sheet})

    session.execute.return_value = _make_execute_result(first=None)
    session.commit.side_effect = Exception("db down")

    with patch("app.services.import_service.load_workbook", return_value=workbook):
        result = await service.import_excel(BytesIO(b"dummy"), user_id)

    assert result["groups_created"] == 0
    assert result["categories_created"] == 0
    assert result["activities_created"] == 0
    assert result["errors"] == ["Database commit failed: db down"]
    session.rollback.assert_awaited_once()


def test_get_default_color_returns_expected_values_and_wraps(session):
    service = ImportService(session)

    assert service._get_default_color(0) == "#FF5733"
    assert service._get_default_color(9) == "#FF3333"
    assert service._get_default_color(10) == "#FF5733"
    assert service._get_default_color(12) == "#3357FF"


@pytest.mark.asyncio
async def test_empty_rows_are_skipped_in_parametre_and_journal(
    service, session, user_id
):
    parametre_sheet = MagicMock()
    parametre_sheet.iter_rows.return_value = [
        None,
        (None, "Work", 1, 0.0, 1.0, 2.0, "hours", "oui"),
        ("Writing", "Work", 1, 0.0, 1.0, 2.0, "hours", "oui"),
    ]

    journal_sheet = MagicMock()
    journal_sheet.iter_rows.return_value = [
        None,
        _make_row(None, 9, 0, 10, 0, "Writing"),
        _make_row(datetime(2026, 1, 21, 0, 0), 9, 0, 10, 0, "Writing"),
    ]

    workbook = _make_workbook(
        ["Paramètre", "Journal"],
        {"Paramètre": parametre_sheet, "Journal": journal_sheet},
    )

    writing_category = MagicMock(spec=Category)
    writing_category.id = uuid4()
    writing_category.name = "Writing"

    session.execute.side_effect = [
        _make_execute_result(first=None),
        _make_execute_result(all_items=[writing_category]),
    ]

    with patch("app.services.import_service.load_workbook", return_value=workbook):
        result = await service.import_excel(BytesIO(b"dummy"), user_id)

    assert result["groups_created"] == 1
    assert result["categories_created"] == 1
    assert result["activities_created"] == 1
    assert result["errors"] == []
