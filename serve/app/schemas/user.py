from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from ..models.region import UserRegion

IdentityRoleId = Literal[
    "balanced",
    "sigma",
    "chaos",
    "pure",
    "max",
    "moka",
    "fan",
    "cat",
    "random",
]


class UserResponse(BaseModel):
    user_id: str
    username: str
    identity_role: IdentityRoleId
    created_at: datetime
    region: UserRegion | None = None
    plaza_display_name: str | None = None


class UpdateIdentityRequest(BaseModel):
    identity_role: IdentityRoleId


class PlazaDisplayNameRequest(BaseModel):
    plaza_display_name: str = Field(..., min_length=1, max_length=24, description="七嘴八舌展示昵称")
