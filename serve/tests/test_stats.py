from datetime import datetime, timezone

from app.services.stats import (
    compute_days_with_records_rate,
    compute_since_last_ms,
    compute_streak_days_no_record,
)


def test_streak_zero_when_today_has_records():
    assert (
        compute_streak_days_no_record(
            date_counts={"2026-05-23": 2},
            today="2026-05-23",
            last_record_date="2026-05-23",
        )
        == 0
    )


def test_streak_counts_from_day_after_last_record():
    assert (
        compute_streak_days_no_record(
            date_counts={"2026-05-19": 1},
            today="2026-05-22",
            last_record_date="2026-05-19",
        )
        == 3
    )


def test_since_last_ms_none_when_no_records():
    assert compute_since_last_ms(None, now_ms=1_000_000) is None


def test_since_last_ms_positive():
    last = datetime(2026, 5, 20, 12, 0, 0, tzinfo=timezone.utc)
    now_ms = int(datetime(2026, 5, 22, 12, 0, 0, tzinfo=timezone.utc).timestamp() * 1000)
    assert compute_since_last_ms(last, now_ms=now_ms) == 2 * 24 * 3600 * 1000


def test_rate_one_day_with_record():
    assert (
        compute_days_with_records_rate(
            user_dates_with_records={"u1": {"2026-05-20", "2026-05-21"}},
            period_dates=["2026-05-20", "2026-05-21"],
            user_ids=["u1"],
        )
        == 1.0
    )
