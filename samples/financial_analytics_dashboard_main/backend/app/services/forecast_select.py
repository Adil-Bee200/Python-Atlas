from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Forecast
from app.services.session_dates import eod_session_key

PROPHET_MODEL_NAME = "prophet_v1"


def pick_active_prophet_forecast(
    session: Session,
    *,
    ticker_id: int,
    last_eod_ts: datetime | None,
) -> Forecast | None:
    """Return the Prophet forecast for the next session after ``last_eod_ts``."""
    rows = session.scalars(
        select(Forecast)
        .where(
            Forecast.ticker_id == ticker_id,
            Forecast.model_name == PROPHET_MODEL_NAME,
            Forecast.predicted_price.is_not(None),
        )
        .order_by(Forecast.generated_at.desc())
    ).all()
    if not rows:
        return None

    if last_eod_ts is None:
        return rows[0]

    last_session = eod_session_key(last_eod_ts)
    for forecast in rows:
        if eod_session_key(forecast.forecast_for) > last_session:
            return forecast

    return max(
        rows,
        key=lambda forecast: (
            eod_session_key(forecast.forecast_for),
            forecast.generated_at,
        ),
    )
