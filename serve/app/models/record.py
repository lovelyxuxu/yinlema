from datetime import datetime, timezone

from pydantic import BaseModel, Field

from .habit import DEFAULT_HABIT, HabitType


class RecordInDB(BaseModel):
    """MongoDB 中存储的行为记录文档结构"""

    id: str | None = Field(default=None, alias="_id")
    user_id: str
    habit_type: HabitType = DEFAULT_HABIT
    timestamp: datetime
    date: str  # YYYY-MM-DD，冗余存储便于日期聚合查询
    note: str = ""
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

    def to_doc(self) -> dict:
        return {
            "user_id": self.user_id,
            "habit_type": self.habit_type,
            "timestamp": self.timestamp,
            "date": self.date,
            "note": self.note,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }

    @classmethod
    def from_doc(cls, doc: dict) -> "RecordInDB":
        if doc and "_id" in doc:
            doc["_id"] = str(doc["_id"])
        if "habit_type" not in doc:
            doc = {**doc, "habit_type": DEFAULT_HABIT}
        if "metadata" not in doc:
            doc = {**doc, "metadata": {}}
        return cls(**doc)
