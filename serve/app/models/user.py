from datetime import datetime, timezone
from typing import Literal

from bson import ObjectId
from pydantic import BaseModel, Field

IdentityRoleId = Literal["balanced", "sigma", "chaos"]


class UserInDB(BaseModel):
    """MongoDB 中存储的用户文档结构"""

    id: str | None = Field(default=None, alias="_id")
    username: str
    password_hash: str
    identity_role: IdentityRoleId = "balanced"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

    def to_doc(self) -> dict:
        """转换为 MongoDB 插入文档（不含 _id）"""
        return {
            "username": self.username,
            "password_hash": self.password_hash,
            "identity_role": self.identity_role,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_doc(cls, doc: dict) -> "UserInDB":
        if doc and "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return cls(**doc)
