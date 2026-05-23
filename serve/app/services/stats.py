from datetime import date, datetime, timedelta, timezone


def _parse(d: str) -> date:
    return date.fromisoformat(d)


def compute_streak_days_no_record(
    *,
    date_counts: dict[str, int],
    today: str,
    last_record_date: str | None,
) -> int:
    if date_counts.get(today, 0) > 0:
        return 0
    if last_record_date is None:
        start = _parse(today)
    else:
        start = _parse(last_record_date) + timedelta(days=1)
    end = _parse(today)
    streak = 0
    d = end
    while d >= start:
        if date_counts.get(d.isoformat(), 0) == 0:
            streak += 1
        else:
            break
        d -= timedelta(days=1)
    return streak


def compute_since_last_ms(last_ts: datetime | None, *, now_ms: int) -> int | None:
    if last_ts is None:
        return None
    if last_ts.tzinfo is None:
        last_ts = last_ts.replace(tzinfo=timezone.utc)
    return max(0, now_ms - int(last_ts.timestamp() * 1000))


def compute_days_with_records_rate(
    *,
    user_dates_with_records: dict[str, set[str]],
    period_dates: list[str],
    user_ids: list[str],
) -> float:
    if not user_ids or not period_dates:
        return 0.0
    period_set = set(period_dates)
    num = 0
    den = len(user_ids) * len(period_dates)
    for uid in user_ids:
        days = user_dates_with_records.get(uid, set()) & period_set
        num += len(days)
    return num / den if den else 0.0


def compute_longest_streak_no_record(
    *,
    sorted_dates_with_any_record: list[str],
    join_date: str,
    today: str,
) -> int:
    if not sorted_dates_with_any_record:
        start = _parse(join_date)
        end = _parse(today)
        return (end - start).days + 1 if end >= start else 0
    best = 0
    cur = 0
    d = _parse(join_date)
    end = _parse(today)
    record_set = set(sorted_dates_with_any_record)
    while d <= end:
        if d.isoformat() not in record_set:
            cur += 1
            best = max(best, cur)
        else:
            cur = 0
        d += timedelta(days=1)
    return best
