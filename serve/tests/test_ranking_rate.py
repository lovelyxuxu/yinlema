from app.services.stats import compute_days_with_records_rate


def test_bucket_rate_two_users_half():
    period = ["2026-05-20", "2026-05-21"]
    rate = compute_days_with_records_rate(
        user_dates_with_records={
            "u1": {"2026-05-20"},
            "u2": set(),
        },
        period_dates=period,
        user_ids=["u1", "u2"],
    )
    assert rate == 0.25
