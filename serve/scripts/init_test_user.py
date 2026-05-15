"""
初始化测试账号与约 3 个月历史鹿记录。

默认账号：luwang / 88888888

用法（在 serve 目录下）：
    python scripts/init_test_user.py

依赖：已配置 serve/.env（或环境变量 MONGODB_URL、MONGODB_DB），且 MongoDB 可连接。
"""

from __future__ import annotations

import os
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

SERVE_ROOT = Path(__file__).resolve().parent.parent
os.chdir(SERVE_ROOT)
sys.path.insert(0, str(SERVE_ROOT))

from pymongo import MongoClient  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.core.security import hash_password  # noqa: E402

TEST_USERNAME = "luwang"
TEST_PASSWORD = "88888888"
# 约 3 个月的自然日跨度（含若干随机波动）
HISTORY_DAYS = 90
RNG_SEED = 42


def _date_str(d: datetime) -> str:
    return d.strftime("%Y-%m-%d")


def main() -> None:
    settings = get_settings()
    client = MongoClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB]
    users = db["users"]
    records = db["records"]

    now = datetime.now(timezone.utc)
    random.seed(RNG_SEED)

    existing = users.find_one({"username": TEST_USERNAME})
    if existing:
        uid_old = str(existing["_id"])
        records.delete_many({"user_id": uid_old})
        users.delete_one({"_id": existing["_id"]})
        print(f"已删除旧测试用户及其记录: {TEST_USERNAME}")

    user_created = now - timedelta(days=HISTORY_DAYS)
    password_hash = hash_password(TEST_PASSWORD)
    user_doc = {
        "username": TEST_USERNAME,
        "password_hash": password_hash,
        "identity_role": "balanced",
        "created_at": user_created,
        "updated_at": now,
    }
    ins = users.insert_one(user_doc)
    user_id = str(ins.inserted_id)
    print(f"已创建用户: {TEST_USERNAME} (_id={user_id})")

    batch: list[dict] = []
    # 从 HISTORY_DAYS 天前一直到「昨天」，生成每日 0~2 条记录（与前端演示类似的可读分布）
    for days_ago in range(HISTORY_DAYS, 0, -1):
        day_start = (now - timedelta(days=days_ago)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        date_s = _date_str(day_start)

        phase_prob = _day_probability(days_ago)
        if random.random() >= phase_prob:
            continue

        times = 2 if random.random() < 0.12 else 1
        for t in range(times):
            hour = random.randint(8, 22)
            minute = random.randint(0, 59)
            ts = day_start.replace(hour=hour, minute=minute)
            batch.append(
                {
                    "user_id": user_id,
                    "timestamp": ts,
                    "date": date_s,
                    "note": "",
                    "created_at": ts,
                }
            )

    if batch:
        records.insert_many(batch)
    print(f"已写入历史记录 {len(batch)} 条（跨度约 {HISTORY_DAYS} 天）")
    client.close()


def _day_probability(days_ago: int) -> float:
    """越早略有更高概率，最近几天略低，便于 streak / 图表有起伏。"""
    if days_ago <= 3:
        return 0.15
    if days_ago <= 14:
        return 0.42
    if days_ago <= 45:
        return 0.48
    return 0.52


if __name__ == "__main__":
    main()
