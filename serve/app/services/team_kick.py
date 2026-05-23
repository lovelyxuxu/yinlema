"""根据自然月无记录天数阈值，将用户踢出小队。"""

from __future__ import annotations

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..core.dates_cn import (
    missed_record_days_calendar_month_naive_shanghai,
    today_local_str,
    parse_local_date,
)
from ..models.habit import DEFAULT_HABIT


async def run_auto_kicks_for_user(db: AsyncIOMotorDatabase, user_id: str) -> None:
    today_s = today_local_str()
    today_d = parse_local_date(today_s)

    memberships = (
        await db["team_members"]
        .find({"user_id": user_id})
        .to_list(length=500)
    )
    if not memberships:
        return

    recs = (
        await db["records"]
        .find(
            {"user_id": user_id, "habit_type": DEFAULT_HABIT},
            {"date": 1},
        )
        .to_list(length=366 * 5)
    )
    record_dates = frozenset(d["date"] for d in recs)

    for m in memberships:
        team_oid = ObjectId(str(m["team_id"]))
        team_doc = await db["teams"].find_one({"_id": team_oid})
        if team_doc is None:
            continue
        threshold = team_doc.get("auto_kick_miss_gt", 20)

        jd = parse_local_date(m["joined_local_date"])
        missed = missed_record_days_calendar_month_naive_shanghai(
            jd, today_d, record_dates
        )
        if missed > threshold and threshold >= 0:
            await db["team_members"].delete_one({"_id": m["_id"]})
