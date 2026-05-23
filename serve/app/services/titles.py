from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class WeekTitle:
    title_id: str
    title_label: str
    title_hint: str


TITLES: list[tuple[str, str]] = [
    ("qingxin", "清新寡欲"),
    ("qingdeng", "青灯古佛"),
    ("danwei", "淡味人生"),
    ("fanxin", "凡心微动"),
    ("shoushua", "手滑常客"),
    ("hehuan", "合欢圣女"),
    ("yinwang", "瘾王本王"),
]


def tier_from_total(week_total: int) -> int:
    if week_total <= 0:
        return 1
    if week_total <= 2:
        return 2
    if week_total <= 5:
        return 3
    if week_total <= 8:
        return 4
    if week_total <= 11:
        return 5
    if week_total <= 15:
        return 6
    return 7


def tier_from_active_days(week_active_days: int) -> int:
    if week_active_days <= 0:
        return 1
    if week_active_days <= 2:
        return 2
    if week_active_days == 3:
        return 3
    if week_active_days == 4:
        return 4
    if week_active_days == 5:
        return 5
    if week_active_days == 6:
        return 6
    return 7


def compute_week_metrics(
    date_count: dict[str, int],
    week_start: date,
    week_end: date,
) -> tuple[int, int]:
    total = 0
    active = 0
    d = week_start
    while d <= week_end:
        c = date_count.get(d.isoformat(), 0)
        if c > 0:
            total += c
            active += 1
        d += timedelta(days=1)
    return total, active


def resolve_title(*, week_total: int, week_active_days: int) -> WeekTitle:
    tier = max(tier_from_total(week_total), tier_from_active_days(week_active_days))
    title_id, title_label = TITLES[tier - 1]
    if tier == 1:
        hint = "本周还没动笔"
    else:
        hint = f"本周 {week_total} 次 · {week_active_days} 天有记录"
    return WeekTitle(title_id=title_id, title_label=title_label, title_hint=hint)
