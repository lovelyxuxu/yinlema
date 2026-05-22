from datetime import datetime, timezone

from pydantic import BaseModel, Field


class TeamInDB(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    name: str
    owner_user_id: str
    # 「自然月缺席打卡天数大于该阈值则踢出」——严格大于阈值才踢（missed_days > threshold）
    auto_kick_miss_gt: int = Field(default=20, ge=0, le=31)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

    def to_doc(self) -> dict:
        return {
            "name": self.name,
            "owner_user_id": self.owner_user_id,
            "auto_kick_miss_gt": self.auto_kick_miss_gt,
            "created_at": self.created_at,
        }

    @classmethod
    def from_doc(cls, doc: dict) -> "TeamInDB":
        if doc and "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return cls(**doc)


class TeamMemberInDB(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    team_id: str
    user_id: str
    joined_local_date: str
    joined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

    def to_doc(self) -> dict:
        return {
            "team_id": self.team_id,
            "user_id": self.user_id,
            "joined_local_date": self.joined_local_date,
            "joined_at": self.joined_at,
        }

    @classmethod
    def from_doc(cls, doc: dict) -> "TeamMemberInDB":
        if doc and "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return cls(**doc)
