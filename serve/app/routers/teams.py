"""小队（无群聊）。"""
from __future__ import annotations

from collections import defaultdict

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..core.database import get_db
from ..core.dates_cn import PeriodLiteral, get_period_bounds, parse_local_date, today_local_str
from ..deps import get_current_user
from ..models.team import TeamInDB, TeamMemberInDB
from ..models.user import UserInDB
from ..schemas.team import (
    TeamCreateRequest,
    TeamDetailResponse,
    TeamMemberItem,
    TeamResponse,
    TeamStatResponse,
)
from ..services.team_kick import run_auto_kicks_for_user


router = APIRouter(prefix="/teams", tags=["小组"])


def _oid(s: str) -> ObjectId:
    try:
        return ObjectId(s)
    except InvalidId as e:
        raise HTTPException(status_code=400, detail="team_id 无效") from e


async def _member_count(db: AsyncIOMotorDatabase, team_hex: str) -> int:
    return await db["team_members"].count_documents({"team_id": team_hex})


async def _build_team_card(
    db: AsyncIOMotorDatabase,
    tdoc: dict,
    current_user_id: str | None = None,
) -> TeamResponse:
    tid = str(tdoc["_id"])
    is_mine = False
    if current_user_id:
        is_mine = await db["team_members"].count_documents(
            {"team_id": tid, "user_id": current_user_id}
        ) > 0
    return TeamResponse(
        team_id=tid,
        name=tdoc["name"],
        owner_user_id=str(tdoc["owner_user_id"]),
        auto_kick_miss_gt=int(tdoc.get("auto_kick_miss_gt", 20)),
        member_count=await _member_count(db, tid),
        created_at=tdoc["created_at"],
        is_mine=is_mine,
    )


@router.get("", response_model=list[TeamResponse])
async def list_teams(
    q: str | None = Query(None, max_length=64),
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> list[TeamResponse]:
    """列出所有小队（广场），可按名称模糊搜索。"""
    filt: dict = {}
    if q and q.strip():
        import re as _re
        filt["name"] = {"$regex": _re.escape(q.strip()), "$options": "i"}
    docs = await db["teams"].find(filt).sort("created_at", -1).to_list(length=200)
    return [await _build_team_card(db, d, current_user.id) for d in docs]


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    body: TeamCreateRequest,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> TeamResponse:
    if not current_user.id:
        raise HTTPException(status_code=400, detail="用户状态异常")

    existing = await db["team_members"].find_one({"user_id": current_user.id})
    if existing:
        raise HTTPException(status_code=409, detail="已加入小队，请先退出后再创建")

    team = TeamInDB(
        name=body.name.strip(),
        owner_user_id=current_user.id,
        auto_kick_miss_gt=body.auto_kick_miss_gt,
    )
    res = await db["teams"].insert_one(team.to_doc())
    tid = str(res.inserted_id)

    await db["team_members"].insert_one(
        TeamMemberInDB(
            team_id=tid,
            user_id=current_user.id,
            joined_local_date=today_local_str(),
        ).to_doc(),
    )

    doc = await db["teams"].find_one({"_id": res.inserted_id})
    return await _build_team_card(db, doc, current_user.id)


@router.get("/mine", response_model=TeamDetailResponse | None)
async def my_team(
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> TeamDetailResponse | None:
    if not current_user.id:
        raise HTTPException(status_code=400, detail="用户状态异常")

    m = await db["team_members"].find_one({"user_id": current_user.id})
    if m is None:
        return None

    team_doc = await db["teams"].find_one({"_id": ObjectId(m["team_id"])})
    if team_doc is None:
        await db["team_members"].delete_one({"_id": m["_id"]})
        return None

    members_docs = (
        await db["team_members"]
        .find({"team_id": m["team_id"]})
        .sort("joined_at", 1)
        .to_list(length=500)
    )
    detail = TeamDetailResponse(
        team=await _build_team_card(db, team_doc, current_user.id),
        members=[
            TeamMemberItem(user_id=x["user_id"], joined_local_date=x["joined_local_date"])
            for x in members_docs
        ],
    )
    return detail


@router.get("/{team_id}", response_model=TeamDetailResponse)
async def get_team(
    team_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> TeamDetailResponse:
    _oid(team_id)

    doc = await db["teams"].find_one({"_id": ObjectId(team_id)})
    if doc is None:
        raise HTTPException(status_code=404, detail="小队不存在")

    members_docs = (
        await db["team_members"]
        .find({"team_id": team_id})
        .sort("joined_at", 1)
        .to_list(length=500)
    )

    return TeamDetailResponse(
        team=await _build_team_card(db, doc, current_user.id),
        members=[
            TeamMemberItem(user_id=x["user_id"], joined_local_date=x["joined_local_date"])
            for x in members_docs
        ],
    )


@router.post("/{team_id}/join", response_model=TeamResponse)
async def join_team(
    team_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> TeamResponse:
    if not current_user.id:
        raise HTTPException(status_code=400, detail="用户状态异常")

    _oid(team_id)

    dup = await db["team_members"].find_one({"user_id": current_user.id})
    if dup:
        raise HTTPException(status_code=409, detail="同一时间只能加入一个小队")

    doc = await db["teams"].find_one({"_id": ObjectId(team_id)})
    if doc is None:
        raise HTTPException(status_code=404, detail="小队不存在")

    await db["team_members"].insert_one(
        TeamMemberInDB(
            team_id=team_id,
            user_id=current_user.id,
            joined_local_date=today_local_str(),
        ).to_doc(),
    )
    await run_auto_kicks_for_user(db, current_user.id)

    refreshed = await db["teams"].find_one({"_id": ObjectId(team_id)})
    if refreshed is None:
        await db["team_members"].delete_one({"team_id": team_id, "user_id": current_user.id})
        raise HTTPException(status_code=500, detail="小队数据异常")

    return await _build_team_card(db, refreshed, current_user.id)


@router.post("/{team_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
async def leave_team(
    team_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> None:
    if not current_user.id:
        raise HTTPException(status_code=400, detail="用户状态异常")

    _oid(team_id)

    res = await db["team_members"].delete_one({"team_id": team_id, "user_id": current_user.id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="未加入该小队或已退出")

    remaining = await _member_count(db, team_id)
    if remaining == 0:
        await db["teams"].delete_one({"_id": ObjectId(team_id)})


async def _team_stats_aggregate(
    db: AsyncIOMotorDatabase,
    team_id: str,
    period: PeriodLiteral,
    anchor_d,
) -> TeamStatResponse:
    start, end = get_period_bounds(anchor_d, period)
    rs, re = start.isoformat(), end.isoformat()

    members = (
        await db["team_members"]
        .find({"team_id": team_id}, {"user_id": 1})
        .to_list(length=500)
    )
    uids = [m["user_id"] for m in members]
    if not uids:
        return TeamStatResponse(
            team_id=team_id,
            period=period,
            anchor=anchor_d.isoformat(),
            range_start=rs,
            range_end=re,
            record_count=0,
            event_rate=0.0,
        )

    from ..core.dates_cn import iter_local_dates_inclusive
    from ..models.habit import DEFAULT_HABIT
    from ..services.stats import compute_days_with_records_rate

    period_dates = iter_local_dates_inclusive(start, end)
    user_dates: defaultdict[str, set[str]] = defaultdict(set)
    rec_count = 0

    async for d in db["records"].find(
        {
            "user_id": {"$in": uids},
            "habit_type": DEFAULT_HABIT,
            "date": {"$gte": rs, "$lte": re},
        },
        {"user_id": 1, "date": 1},
    ):
        rec_count += 1
        user_dates[d["user_id"]].add(d["date"])

    rate = compute_days_with_records_rate(
        user_dates_with_records=dict(user_dates),
        period_dates=period_dates,
        user_ids=uids,
    )

    return TeamStatResponse(
        team_id=team_id,
        period=period,
        anchor=anchor_d.isoformat(),
        range_start=rs,
        range_end=re,
        record_count=rec_count,
        event_rate=round(rate, 6),
    )


@router.get("/{team_id}/stats", response_model=TeamStatResponse)
async def team_stats_endpoint(
    team_id: str,
    period: PeriodLiteral = Query("week"),
    anchor: str | None = Query(None),
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> TeamStatResponse:
    _oid(team_id)
    doc = await db["teams"].find_one({"_id": ObjectId(team_id)})
    if doc is None:
        raise HTTPException(status_code=404, detail="小队不存在")

    day_s = (anchor or "").strip() or today_local_str()
    try:
        anchor_d = parse_local_date(day_s)
    except ValueError as e:
        raise HTTPException(status_code=422, detail="anchor 须为 YYYY-MM-DD") from e

    return await _team_stats_aggregate(db, team_id, period, anchor_d)
