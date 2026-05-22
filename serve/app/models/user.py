from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

from .region import UserRegion

IdentityRoleId = Literal["balanced", "sigma", "chaos"]


class UserInDB(BaseModel):
    """MongoDB 中存储的用户文档结构"""

    id: str | None = Field(default=None, alias="_id")
    username: str
    password_hash: str
    identity_role: IdentityRoleId = "balanced"
    region: UserRegion | None = None
    plaza_display_name: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

    def to_doc(self) -> dict:
        """转换为 MongoDB 插入文档（不含 _id）"""
        d: dict = {
            "username": self.username,
            "password_hash": self.password_hash,
            "identity_role": self.identity_role,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if self.region is not None:
            d["region"] = self.region.mongo_dict()
        if self.plaza_display_name is not None:
            d["plaza_display_name"] = self.plaza_display_name
        return d

    @classmethod
    def from_doc(cls, doc: dict) -> "UserInDB":
        if doc:
            oid = doc.get("_id")
            if oid is not None:
                doc["_id"] = str(oid)
            rg = doc.get("region")
            if rg and isinstance(rg, dict):
                try:
                    doc["region"] = UserRegion(**rg)
                except ValidationError:
                    doc["region"] = None
            elif rg is None:
                doc.pop("region", None)
            else:
                doc["region"] = None
            if doc.get("plaza_display_name") is None:
                doc.pop("plaza_display_name", None)
        return cls(**doc)
