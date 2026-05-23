from datetime import datetime

from pydantic import BaseModel, Field

from ..models.habit import DEFAULT_HABIT, HabitType


class CreateRecordRequest(BaseModel):
    timestamp: datetime = Field(..., description="发生时间（ISO8601）")
    note: str = Field(default="", max_length=500, description="备注（可选）")
    habit_type: HabitType = Field(default=DEFAULT_HABIT, description="习惯类型")


class UpdateRecordRequest(BaseModel):
    note: str = Field(..., max_length=500, description="备注内容")


class RecordResponse(BaseModel):
    record_id: str
    user_id: str
    habit_type: HabitType
    timestamp: datetime
    date: str
    note: str
    created_at: datetime


class DayStatItem(BaseModel):
    date: str
    count: int


class WeekStatItem(BaseModel):
    label: str
    count: int


class MonthStatItem(BaseModel):
    label: str
    count: int


class StatsResponse(BaseModel):
    streak_days_no_record: int
    since_last_ms: int | None = None
    today_count: int
    longest_streak_no_record: int = 0
    recent_frequency: float
    by_day: list[DayStatItem]
    by_week: list[WeekStatItem]
    by_month: list[MonthStatItem]
