from datetime import date

from app.services.titles import (
    compute_week_metrics,
    resolve_title,
    tier_from_active_days,
    tier_from_total,
)


def test_tier_from_total_boundaries():
    assert tier_from_total(0) == 1
    assert tier_from_total(2) == 2
    assert tier_from_total(5) == 3
    assert tier_from_total(8) == 4
    assert tier_from_total(11) == 5
    assert tier_from_total(15) == 6
    assert tier_from_total(16) == 7


def test_tier_from_active_days_boundaries():
    assert tier_from_active_days(0) == 1
    assert tier_from_active_days(2) == 2
    assert tier_from_active_days(3) == 3
    assert tier_from_active_days(7) == 7


def test_resolve_title_qingxin_zero_week():
    t = resolve_title(week_total=0, week_active_days=0)
    assert t.title_id == "qingxin"
    assert t.title_label == "清新寡欲"
    assert t.title_hint == "本周还没动笔"


def test_resolve_title_max_of_two_axes():
    t = resolve_title(week_total=2, week_active_days=5)
    assert t.title_id == "shoushua"
    assert t.title_label == "手滑常客"


def test_compute_week_metrics_iso_monday_week():
    date_count = {
        "2026-05-18": 2,
        "2026-05-20": 1,
    }
    start = date(2026, 5, 18)
    end = date(2026, 5, 24)
    total, active = compute_week_metrics(date_count, start, end)
    assert total == 3
    assert active == 2
