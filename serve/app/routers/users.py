from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..core.database import get_db
from ..deps import get_current_user
from ..models.user import UserInDB
from ..schemas.user import (
    PlazaDisplayNameRequest,
    UserResponse,
    UpdateIdentityRequest,
)

router = APIRouter(prefix="/users", tags=["用户"])


@router.put(
    "/me/identity",
    response_model=UserResponse,
    summary="更新身份角色",
    description="切换当前用户的「今日鹿么」随机概率角色（平常心 / 西格玛男人 / 混沌乐子人）",
)
async def update_identity(
    body: UpdateIdentityRequest,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> UserResponse:
    now = datetime.now(timezone.utc)
    await db["users"].update_one(
        {"_id": ObjectId(current_user.id)},
        {"$set": {"identity_role": body.identity_role, "updated_at": now}},
    )
    return UserResponse(
        user_id=current_user.id or "",
        username=current_user.username,
        identity_role=body.identity_role,
        created_at=current_user.created_at,
        region=current_user.region,
        plaza_display_name=current_user.plaza_display_name,
    )


@router.patch(
    "/me/display-name",
    response_model=UserResponse,
    summary="设置广场展示昵称",
)
async def update_display_name(
    body: PlazaDisplayNameRequest,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> UserResponse:
    now = datetime.now(timezone.utc)
    await db["users"].update_one(
        {"_id": ObjectId(current_user.id)},
        {"$set": {"plaza_display_name": body.plaza_display_name.strip(), "updated_at": now}},
    )
    updated = UserInDB.from_doc(
        await db["users"].find_one({"_id": ObjectId(current_user.id)})
    )
    return UserResponse(
        user_id=updated.id or "",
        username=updated.username,
        identity_role=updated.identity_role,
        created_at=updated.created_at,
        region=updated.region,
        plaza_display_name=updated.plaza_display_name,
    )
