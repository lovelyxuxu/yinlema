"""中国（上海）日历日工具：打卡与排行统一使用 Asia/Shanghai 的 YYYY-MM-DD。"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Literal
from zoneinfo import ZoneInfo

TZ_SHANGHAI = ZoneInfo("Asia/Shanghai")

PeriodLiteral = Literal["day", "week", "month", "year"]
ScopeLiteral = Literal["province", "city", "district", "team"]
MetricLiteral = Literal["rate", "count"]

BACKFILL_MAX_DAYS = 90


def now_shanghai() -> datetime:
    return datetime.now(TZ_SHANGHAI)


def today_local_str() -> str:
    """当前上海日历日字符串。"""
    return now_shanghai().date().isoformat()


def datetime_to_local_date(dt: datetime) -> str:
    """将带时区的时刻转为上海日历日 YYYY-MM-DD。"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt.astimezone(TZ_SHANGHAI).date().isoformat()


def parse_local_date(s: str) -> date:
    return date.fromisoformat(s.strip())


def get_period_bounds(
    anchor: date,
    period: PeriodLiteral,
) -> tuple[date, date]:
    """闭区间 [start, end]，均为上海本地日历日。"""
    if period == "day":
        return anchor, anchor
    if period == "week":
        # ISO 周一为一周之始
        start = anchor - timedelta(days=(anchor.weekday()))
        end = start + timedelta(days=6)
        return start, end
    if period == "month":
        start = anchor.replace(day=1)
        if anchor.month == 12:
            nxt = anchor.replace(year=anchor.year + 1, month=1, day=1)
        else:
            nxt = anchor.replace(month=anchor.month + 1, day=1)
        end = nxt - timedelta(days=1)
        return start, end
    if period == "year":
        start = date(anchor.year, 1, 1)
        end = date(anchor.year, 12, 31)
        return start, end
    raise ValueError(period)


def ym_tuple(d: date) -> tuple[int, int]:
    return d.year, d.month


def iter_local_dates_inclusive(start: date, end: date) -> list[str]:
    """闭区间内每个上海日历日 YYYY-MM-DD。"""
    out: list[str] = []
    d = start
    while d <= end:
        out.append(d.isoformat())
        d += timedelta(days=1)
    return out


def missed_record_days_calendar_month_naive_shanghai(
    joined_local_date: date,
    today_local: date,
    record_dates_set: frozenset[str],
) -> int:
    """自然月内无行为记录的天数（用于小队自动踢人）。"""
    month_first = date(today_local.year, today_local.month, 1)
    effective_start = max(month_first, joined_local_date)
    missed = 0
    d = effective_start
    while d <= today_local:
        if d.isoformat() not in record_dates_set:
            missed += 1
        d += timedelta(days=1)
    return missed


def missed_checkins_calendar_month_naive_shanghai(
    joined_local_date: date,
    today_local: date,
    check_in_dates_set: frozenset[str],
) -> int:
    """
    自然月口径：从今天所在月的 1 号起至「今天」（含），与加入日历日较晚者为本区间起点；
    区间内没有打卡条目的日历日计为缺席一天。
    """
    month_first = date(today_local.year, today_local.month, 1)
    effective_start = max(month_first, joined_local_date)
    missed = 0
    d = effective_start
    while d <= today_local:
        if d.isoformat() not in check_in_dates_set:
            missed += 1
        d += timedelta(days=1)
    return missed
