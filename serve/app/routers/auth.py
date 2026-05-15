from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..core.database import get_db
from ..core.security import hash_password, verify_password, create_access_token
from ..models.user import UserInDB
from ..schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from ..schemas.user import UserResponse
from ..deps import get_current_user

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="注册账号",
)
async def register(
    body: RegisterRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> TokenResponse:
    existing = await db["users"].find_one({"username": body.username})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="用户名已被占用",
        )

    user = UserInDB(
        username=body.username,
        password_hash=hash_password(body.password),
    )
    result = await db["users"].insert_one(user.to_doc())
    user_id = str(result.inserted_id)

    token = create_access_token(subject=user_id)
    return TokenResponse(
        access_token=token,
        user_id=user_id,
        username=user.username,
        identity_role=user.identity_role,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="账号登录",
)
async def login(
    body: LoginRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> TokenResponse:
    doc = await db["users"].find_one({"username": body.username})
    if doc is None or not verify_password(body.password, doc["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    user_id = str(doc["_id"])
    token = create_access_token(subject=user_id)
    return TokenResponse(
        access_token=token,
        user_id=user_id,
        username=doc["username"],
        identity_role=doc["identity_role"],
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="获取当前登录用户信息",
)
async def get_me(
    current_user: UserInDB = Depends(get_current_user),
) -> UserResponse:
    return UserResponse(
        user_id=current_user.id,
        username=current_user.username,
        identity_role=current_user.identity_role,
        created_at=current_user.created_at,
    )
