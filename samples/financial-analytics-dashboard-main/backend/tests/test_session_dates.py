from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.services.session_dates import (
    eod_session_key,
    is_settled_eod_session,
    next_trading_session_key,
    session_midnight_utc,
)

ET = ZoneInfo("America/New_York")


def test_eod_session_key_anchors_midnight_et_bar() -> None:
    ts = datetime(2026, 6, 15, 4, 0, tzinfo=timezone.utc)
    assert eod_session_key(ts) == "2026-06-15"


def test_eod_session_key_uses_et_date_not_utc() -> None:
    # 02:00 UTC on the 15th is still the 14th in ET (evening).
    ts = datetime(2026, 6, 15, 2, 0, tzinfo=timezone.utc)
    assert eod_session_key(ts) == "2026-06-14"


def test_next_trading_session_skips_weekend() -> None:
    assert next_trading_session_key("2026-06-12") == "2026-06-15"
    assert next_trading_session_key("2026-06-15") == "2026-06-16"


def test_is_settled_rejects_today_before_close() -> None:
    now = datetime(2026, 6, 16, 7, 38, tzinfo=timezone.utc)  # 03:38 ET
    assert is_settled_eod_session("2026-06-15", now=now) is True
    assert is_settled_eod_session("2026-06-16", now=now) is False


def test_is_settled_accepts_today_after_close() -> None:
    now = datetime(2026, 6, 15, 22, 5, tzinfo=ET).astimezone(timezone.utc)
    assert is_settled_eod_session("2026-06-15", now=now) is True


def test_session_midnight_utc_matches_forecast_for() -> None:
    assert session_midnight_utc("2026-06-16") == datetime(
        2026, 6, 16, 4, 0, tzinfo=timezone.utc
    )
