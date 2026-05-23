from datetime import datetime, timedelta, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..core.database import get_db
from ..core.dates_cn import datetime_to_local_date, parse_local_date, today_local_str
from ..deps import get_current_user
from ..models.habit import DEFAULT_HABIT, HabitType
from ..models.record import RecordInDB
from ..models.user import UserInDB
from ..schemas.record import (
    CreateRecordRequest,
    UpdateRecordRequest,
    RecordResponse,
    StatsResponse,
    DayStatItem,
    WeekStatItem,
    MonthStatItem,
)
from ..services.stats import (
    compute_longest_streak_no_record,
    compute_since_last_ms,
    compute_streak_days_no_record,
)

router = APIRouter(prefix="/records", tags=["行为记录"])


def _date_str(d: datetime) -> str:
    return d.strftime("%Y-%m-%d")


def _habit_filter(user_id: str, habit_type: HabitType) -> dict:
    return {"user_id": user_id, "habit_type": habit_type}


def _to_response(doc: dict) -> RecordResponse:
    return RecordResponse(
        record_id=str(doc["_id"]),
        user_id=doc["user_id"],
        habit_type=doc.get("habit_type", DEFAULT_HABIT),
        timestamp=doc["timestamp"],
        date=doc["date"],
        note=doc.get("note", ""),
        created_at=doc["created_at"],
    )


@router.get("", response_model=list[RecordResponse], summary="获取记录列表")
async def list_records(
    limit: int = Query(default=50, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    habit_type: HabitType = Query(default=DEFAULT_HABIT),
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> list[RecordResponse]:
    cursor = (
        db["records"]
        .find(_habit_filter(current_user.id, habit_type))
        .sort("timestamp", -1)
        .skip(offset)
        .limit(limit)
    )
    docs = await cursor.to_list(length=limit)
    return [_to_response(d) for d in docs]


@router.post(
    "",
    response_model=RecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="新增一条记录",
)
async def create_record(
    body: CreateRecordRequest,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> RecordResponse:
    now_utc = datetime.now(timezone.utc)
    ts = body.timestamp
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    if ts > now_utc + timedelta(minutes=1):
        raise HTTPException(status_code=400, detail="时间不能在未来")

    record = RecordInDB(
        user_id=current_user.id,
        habit_type=body.habit_type,
        timestamp=ts,
        date=datetime_to_local_date(ts),
        note=body.note,
    )
    result = await db["records"].insert_one(record.to_doc())
    doc = await db["records"].find_one({"_id": result.inserted_id})
    return _to_response(doc)


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除记录")
async def delete_record(
    record_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> None:
    try:
        oid = ObjectId(record_id)
    except Exception:
        raise HTTPException(status_code=400, detail="record_id 格式错误")

    result = await db["records"].delete_one({"_id": oid, "user_id": current_user.id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="记录不存在或无权删除")


@router.patch("/{record_id}", response_model=RecordResponse, summary="更新记录备注")
async def update_record(
    record_id: str,
    body: UpdateRecordRequest,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> RecordResponse:
    try:
        oid = ObjectId(record_id)
    except Exception:
        raise HTTPException(status_code=400, detail="record_id 格式错误")

    doc = await db["records"].find_one({"_id": oid, "user_id": current_user.id})
    if doc is None:
        raise HTTPException(status_code=404, detail="记录不存在或无权修改")

    await db["records"].update_one({"_id": oid}, {"$set": {"note": body.note}})
    doc["note"] = body.note
    return _to_response(doc)


@router.get("/stats", response_model=StatsResponse, summary="获取统计数据")
async def get_stats(
    habit_type: HabitType = Query(default=DEFAULT_HABIT),
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> StatsResponse:
    today_str = today_local_str()
    join_date_str = datetime_to_local_date(current_user.created_at)
    filt = _habit_filter(current_user.id, habit_type)

    since = datetime.now(timezone.utc) - timedelta(days=90)
    cursor = db["records"].find(
        {**filt, "timestamp": {"$gte": since}},
        {"date": 1, "timestamp": 1},
    )
    docs = await cursor.to_list(length=10000)

    date_count: dict[str, int] = {}
    last_ts: datetime | None = None
    for d in docs:
        date_count[d["date"]] = date_count.get(d["date"], 0) + 1
        ts = d["timestamp"]
        if last_ts is None or ts > last_ts:
            last_ts = ts

    last_doc = await db["records"].find_one(filt, sort=[("timestamp", -1)])
    if last_doc and (last_ts is None or last_doc["timestamp"] > last_ts):
        last_ts = last_doc["timestamp"]

    last_record_date = datetime_to_local_date(last_ts) if last_ts else None

    streak = compute_streak_days_no_record(
        date_counts=date_count,
        today=today_str,
        last_record_date=last_record_date,
    )
    since_last_ms = compute_since_last_ms(
        last_ts,
        now_ms=int(datetime.now(timezone.utc).timestamp() * 1000),
    )
    longest = compute_longest_streak_no_record(
        sorted_dates_with_any_record=sorted(date_count.keys()),
        join_date=join_date_str,
        today=today_str,
    )

    today_count = date_count.get(today_str, 0)
    date_set = set(date_count.keys())

    recent_days = [
        _date_str(datetime.now(timezone.utc) - timedelta(days=i))
        for i in range(7)
    ]
    recent_frequency = sum(1 for d in recent_days if d in date_set) / 7

    by_day = [
        DayStatItem(date=d, count=date_count.get(d, 0))
        for d in reversed(recent_days)
    ]

    by_week: list[WeekStatItem] = []
    for i in range(5, -1, -1):
        end = datetime.now(timezone.utc) - timedelta(days=i * 7)
        start = end - timedelta(days=6)
        count = sum(
            date_count.get(_date_str(start + timedelta(days=j)), 0)
            for j in range(7)
        )
        label = f"{start.month}/{start.day}"
        by_week.append(WeekStatItem(label=label, count=count))

    by_month: list[MonthStatItem] = []
    now = datetime.now(timezone.utc)
    for i in range(5, -1, -1):
        month = (now.month - i - 1) % 12 + 1
        year = now.year + ((now.month - i - 1) // 12)
        prefix = f"{year}-{str(month).zfill(2)}"
        count = sum(v for k, v in date_count.items() if k.startswith(prefix))
        by_month.append(MonthStatItem(label=f"{month}月", count=count))

    return StatsResponse(
        streak_days_no_record=streak,
        since_last_ms=since_last_ms,
        today_count=today_count,
        longest_streak_no_record=longest,
        recent_frequency=round(recent_frequency, 4),
        by_day=by_day,
        by_week=by_week,
        by_month=by_month,
    )
