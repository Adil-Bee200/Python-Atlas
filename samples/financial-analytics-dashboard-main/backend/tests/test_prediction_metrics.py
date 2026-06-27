from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

from app.services.prediction_metrics import (
    NAIVE_MODEL_NAME,
    PROPHET_MODEL_NAME,
    _aggregate_ticker_mae,
)
from app.services.session_dates import session_midnight_utc


def _metric_row(session_key: str, *, model_name: str, absolute_error: float):
    return SimpleNamespace(
        model_name=model_name,
        date=session_midnight_utc(session_key),
        absolute_error=absolute_error,
    )


def test_aggregate_ticker_mae_returns_window_mae() -> None:
    rows = [
        _metric_row("2026-06-10", model_name=PROPHET_MODEL_NAME, absolute_error=2.0),
        _metric_row("2026-06-11", model_name=PROPHET_MODEL_NAME, absolute_error=4.0),
        _metric_row("2026-06-12", model_name=PROPHET_MODEL_NAME, absolute_error=6.0),
        _metric_row("2026-06-12", model_name=NAIVE_MODEL_NAME, absolute_error=8.0),
    ]

    models = _aggregate_ticker_mae(rows)
    prophet = next(m for m in models if m.model_name == PROPHET_MODEL_NAME)
    naive = next(m for m in models if m.model_name == NAIVE_MODEL_NAME)

    assert prophet.mae_7d == 4.0
    assert prophet.samples_7d == 3
    assert naive.mae_7d == 8.0
    assert naive.samples_7d == 1


def test_aggregate_ticker_mae_uses_eod_session_key() -> None:
    # Regression: must not reference removed _eod_session_key helper.
    rows = [
        _metric_row(
            "2026-06-15",
            model_name=PROPHET_MODEL_NAME,
            absolute_error=1.0,
        ),
    ]
    models = _aggregate_ticker_mae(rows)
    prophet = next(m for m in models if m.model_name == PROPHET_MODEL_NAME)
    assert prophet.mae_7d == 1.0
    assert prophet.samples_7d == 1
