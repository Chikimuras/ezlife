from __future__ import annotations

import re
from datetime import date as date_type
from datetime import datetime, time
from typing import Literal
from uuid import UUID

from pydantic import field_validator

from app.schemas.base import CamelModel


class GroupBase(CamelModel):
    name: str
    color: str | None = None

    @field_validator("color")
    @classmethod
    def validate_hex_color(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not re.match(r"^#[0-9A-Fa-f]{6}$", v):
            raise ValueError("Color must be in hex format (#RRGGBB)")
        return v.upper()


class GroupCreate(GroupBase):
    pass


class GroupUpdate(CamelModel):
    name: str | None = None
    color: str | None = None

    @field_validator("color")
    @classmethod
    def validate_hex_color(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not re.match(r"^#[0-9A-Fa-f]{6}$", v):
            raise ValueError("Color must be in hex format (#RRGGBB)")
        return v.upper()


class GroupResponse(GroupBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


class CategoryBase(CamelModel):
    name: str
    group_id: UUID
    priority: int = 1
    min_weekly_hours: float = 0
    target_weekly_hours: float = 0
    max_weekly_hours: float = 0
    unit: Literal["hours", "minutes", "count"] = "hours"
    mandatory: bool = False


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CamelModel):
    name: str | None = None
    group_id: UUID | None = None
    priority: int | None = None
    min_weekly_hours: float | None = None
    target_weekly_hours: float | None = None
    max_weekly_hours: float | None = None
    unit: Literal["hours", "minutes", "count"] | None = None
    mandatory: bool | None = None


class CategoryResponse(CategoryBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


class GlobalConstraintsBase(CamelModel):
    total_weekly_hours: float = 168.0
    min_sleep_hours: float = 56.0
    underutilization_threshold: float = 0.8
    overutilization_threshold: float = 1.2
    wasted_time_threshold: float = 2.0


class GlobalConstraintsUpdate(CamelModel):
    total_weekly_hours: float | None = None
    min_sleep_hours: float | None = None
    underutilization_threshold: float | None = None
    overutilization_threshold: float | None = None
    wasted_time_threshold: float | None = None


class GlobalConstraintsResponse(GlobalConstraintsBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


class ActivityBase(CamelModel):
    date: date_type
    start_time: time
    end_time: time
    category_id: UUID
    notes: str | None = None

    @field_validator("start_time", "end_time", mode="before")
    @classmethod
    def validate_time_format(cls, v):
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
    def validate_end_time_after_start(cls, v, info):
        if "start_time" in info.data and info.data["start_time"] >= v:
            raise ValueError("end_time must be after start_time")
        return v


class ActivityCreate(ActivityBase):
    pass


class ActivityUpdate(CamelModel):
    date: date_type | None = None
    start_time: time | None = None
    end_time: time | None = None
    category_id: UUID | None = None
    notes: str | None = None

    @field_validator("start_time", "end_time", mode="before")
    @classmethod
    def validate_time_format(cls, v):
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

    @field_validator("end_time")
    @classmethod
    def validate_end_time_after_start(cls, v, info):
        if v is None:
            return v
        if "start_time" in info.data and info.data["start_time"] is not None:
            if info.data["start_time"] >= v:
                raise ValueError("end_time must be after start_time")
        return v


class ActivityResponse(ActivityBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
