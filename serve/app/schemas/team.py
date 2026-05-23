from datetime import datetime

from pydantic import BaseModel, Field


class TeamCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=32)
    auto_kick_miss_gt: int = Field(default=20, ge=0, le=31)


class TeamResponse(BaseModel):
    team_id: str
    name: str
    owner_user_id: str
    auto_kick_miss_gt: int
    member_count: int
    created_at: datetime
    is_mine: bool = False


class TeamMemberItem(BaseModel):
    user_id: str
    joined_local_date: str


class TeamDetailResponse(BaseModel):
    team: TeamResponse
    members: list[TeamMemberItem]


class TeamStatResponse(BaseModel):
    team_id: str
    period: str
    anchor: str
    range_start: str
    range_end: str
    record_count: int
    event_rate: float
