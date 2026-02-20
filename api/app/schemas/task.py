from __future__ import annotations

import re
from datetime import date as date_type
from datetime import datetime, time
from typing import Literal
from uuid import UUID

from pydantic import field_validator

from app.schemas.base import CamelModel

# ── TaskList ──────────────────────────────────────────────────────────


class TaskListCreate(CamelModel):
    name: str
    color: str | None = None
    icon: str | None = None
    position: int = 0

    @field_validator("color")
    @classmethod
    def validate_hex_color(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not re.match(r"^#[0-9A-Fa-f]{6}$", v):
            raise ValueError("Color must be in hex format (#RRGGBB)")
        return v.upper()


class TaskListUpdate(CamelModel):
    name: str | None = None
    color: str | None = None
    icon: str | None = None
    position: int | None = None

    @field_validator("color")
    @classmethod
    def validate_hex_color(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not re.match(r"^#[0-9A-Fa-f]{6}$", v):
            raise ValueError("Color must be in hex format (#RRGGBB)")
        return v.upper()


class TaskListResponse(CamelModel):
    id: UUID
    name: str
    color: str | None
    icon: str | None
    position: int
    task_count: int = 0
    created_at: datetime
    updated_at: datetime


# ── Task ──────────────────────────────────────────────────────────────


class TaskCreate(CamelModel):
    task_list_id: UUID
    category_id: UUID | None = None
    title: str
    description: str | None = None
    priority: Literal["low", "medium", "high", "urgent"] = "medium"
    due_date: date_type | None = None
    scheduled_date: date_type | None = None
    scheduled_start_time: time | None = None
    scheduled_end_time: time | None = None
    estimated_duration_minutes: int | None = None
    recurrence_rule: str | None = None
    exception_dates: list[str] | None = None
    position: int = 0

    @field_validator("scheduled_start_time", "scheduled_end_time", mode="before")
    @classmethod
    def validate_time_format(cls, v: str | time | None) -> time | None:
        if v is None:
            return v
        if isinstance(v, time):
            return v
        if isinstance(v, str):
            if not re.match(r"^([01]\d|2[0-3]):([0-5]\d)$", v):
                raise ValueError("Time must be in HH:mm format (00:00 to 23:59)")
            hours, minutes = v.split(":")
            return time(int(hours), int(minutes))
        return v

    @field_validator("scheduled_end_time")
    @classmethod
    def validate_end_after_start(cls, v: time | None, info) -> time | None:
        if v is None:
            return v
        start = info.data.get("scheduled_start_time")
        if start is not None and start >= v:
            raise ValueError("scheduled_end_time must be after scheduled_start_time")
        return v

    @field_validator("estimated_duration_minutes")
    @classmethod
    def validate_positive_duration(cls, v: int | None) -> int | None:
        if v is not None and v <= 0:
            raise ValueError("Estimated duration must be positive")
        return v


class TaskUpdate(CamelModel):
    task_list_id: UUID | None = None
    category_id: UUID | None = None
    title: str | None = None
    description: str | None = None
    status: Literal["todo", "in_progress", "done"] | None = None
    priority: Literal["low", "medium", "high", "urgent"] | None = None
    due_date: date_type | None = None
    scheduled_date: date_type | None = None
    scheduled_start_time: time | None = None
    scheduled_end_time: time | None = None
    estimated_duration_minutes: int | None = None
    recurrence_rule: str | None = None
    exception_dates: list[str] | None = None
    position: int | None = None

    @field_validator("scheduled_start_time", "scheduled_end_time", mode="before")
    @classmethod
    def validate_time_format(cls, v: str | time | None) -> time | None:
        if v is None:
            return v
        if isinstance(v, time):
            return v
        if isinstance(v, str):
            if not re.match(r"^([01]\d|2[0-3]):([0-5]\d)$", v):
                raise ValueError("Time must be in HH:mm format (00:00 to 23:59)")
            hours, minutes = v.split(":")
            return time(int(hours), int(minutes))
        return v


class TaskResponse(CamelModel):
    id: UUID
    task_list_id: UUID
    category_id: UUID | None
    title: str
    description: str | None
    status: str
    priority: str
    due_date: date_type | None
    scheduled_date: date_type | None
    scheduled_start_time: time | None
    scheduled_end_time: time | None
    estimated_duration_minutes: int | None
    recurrence_rule: str | None
    exception_dates: list[str] | None
    position: int
    activity_ids: list[UUID] = []
    created_at: datetime
    updated_at: datetime


# ── Task Completion / Convert to Activity ─────────────────────────────


class TaskCompleteRequest(CamelModel):
    add_to_tracker: bool = False
    date: date_type | None = None
    start_time: time | None = None
    end_time: time | None = None
    category_id: UUID | None = None
    notes: str | None = None

    @field_validator("start_time", "end_time", mode="before")
    @classmethod
    def validate_time_format(cls, v: str | time | None) -> time | None:
        if v is None:
            return v
        if isinstance(v, time):
            return v
        if isinstance(v, str):
            if not re.match(r"^([01]\d|2[0-3]):([0-5]\d)$", v):
                raise ValueError("Time must be in HH:mm format (00:00 to 23:59)")
            hours, minutes = v.split(":")
            return time(int(hours), int(minutes))
        return v


class ConvertToActivityRequest(CamelModel):
    date: date_type
    start_time: time
    end_time: time
    category_id: UUID | None = None
    notes: str | None = None

    @field_validator("start_time", "end_time", mode="before")
    @classmethod
    def validate_time_format(cls, v: str | time) -> time:
        if isinstance(v, time):
            return v
        if isinstance(v, str):
            if not re.match(r"^([01]\d|2[0-3]):([0-5]\d)$", v):
                raise ValueError("Time must be in HH:mm format (00:00 to 23:59)")
            hours, minutes = v.split(":")
            return time(int(hours), int(minutes))
        return v

    @field_validator("end_time")
    @classmethod
    def validate_end_after_start(cls, v: time, info) -> time:
        start = info.data.get("start_time")
        if start is not None and start >= v:
            raise ValueError("end_time must be after start_time")
        return v


class TaskActivityResponse(CamelModel):
    id: UUID
    task_id: UUID
    activity_id: UUID
    created_at: datetime


class GenerateOccurrencesRequest(CamelModel):
    count: int = 10
    exception_dates: list[str] | None = None
