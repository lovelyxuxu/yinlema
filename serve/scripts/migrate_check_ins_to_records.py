"""
将 check_ins.status==deer 且当日无 record 的条目补写为 records（幂等）。

用法: cd serve && python scripts/migrate_check_ins_to_records.py
"""
from __future__ import annotations

import asyncio
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import connect_db, close_db, get_db
from app.models.habit import DEFAULT_HABIT
from app.models.record import RecordInDB

TZ = ZoneInfo("Asia/Shanghai")


async def main() -> None:
    await connect_db()
    db = get_db()
    inserted = 0
    skipped = 0

    async for ci in db["check_ins"].find({"status": "deer"}):
        uid = ci["user_id"]
        local_date = ci["local_date"]
        exists = await db["records"].find_one(
            {"user_id": uid, "date": local_date, "habit_type": DEFAULT_HABIT}
        )
        if exists:
            skipped += 1
            continue
        ts = datetime.fromisoformat(f"{local_date}T12:00:00").replace(tzinfo=TZ)
        record = RecordInDB(
            user_id=uid,
            habit_type=DEFAULT_HABIT,
            timestamp=ts,
            date=local_date,
            note="migrated from check_in",
        )
        await db["records"].insert_one(record.to_doc())
        inserted += 1

    print(f"migrate_check_ins_to_records: inserted={inserted} skipped={skipped}")
    await close_db()


if __name__ == "__main__":
    asyncio.run(main())
