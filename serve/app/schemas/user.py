from datetime import datetime
from typing import Literal

from pydantic import BaseModel

IdentityRoleId = Literal["balanced", "sigma", "chaos"]


class UserResponse(BaseModel):
    user_id: str
    username: str
    identity_role: IdentityRoleId
    created_at: datetime


class UpdateIdentityRequest(BaseModel):
    identity_role: IdentityRoleId
