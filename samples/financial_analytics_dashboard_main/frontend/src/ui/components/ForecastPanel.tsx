import type { ForecastPoint } from "../../api/client";
import { fmtForecastFor, fmtMarketDate, fmtPrice } from "../../utils/format";
import { pickProphetForecast } from "../../utils/forecasts";

const PROPHET_MODEL = "prophet_v1";

export { pickProphetForecast };

type Props = {
  forecast: ForecastPoint | null | undefined;
  fallbackPrice?: number | null;
  compact?: boolean;
};

export function ForecastPanel({ forecast, fallbackPrice, compact }: Props) {
  const price = forecast?.predicted_close ?? fallbackPrice ?? null;
  const modelLabel =
    forecast?.model_version === PROPHET_MODEL
      ? "Prophet forecast"
      : forecast?.model_version ?? "Forecast";

  const targetLabel = forecast?.forecast_for
    ? `For ${fmtForecastFor(forecast.forecast_for)}`
    : "Next session";

  const hasInterval =
    forecast?.lower_bound != null &&
    forecast?.upper_bound != null &&
    forecast.lower_bound !== forecast.upper_bound;

  return (
    <div className={`forecast-box${compact ? " forecast-box--compact" : ""}`}>
      <span className="label">{modelLabel}</span>
      <span className="forecast-date">{targetLabel}</span>
      <span className="value">{fmtPrice(price)}</span>
      {hasInterval && (
        <div className="forecast-interval">
          <span className="forecast-interval__title">95% confidence interval</span>
          <span className="forecast-interval__row">
            <span className="forecast-interval__label">Lower</span>
            <span className="forecast-interval__value">
              {fmtPrice(forecast.lower_bound)}
            </span>
          </span>
          <span className="forecast-interval__row">
            <span className="forecast-interval__label">Upper</span>
            <span className="forecast-interval__value">
              {fmtPrice(forecast.upper_bound)}
            </span>
          </span>
        </div>
      )}
      <span className="meta">
        {forecast ? `Updated ${fmtMarketDate(forecast.created_at)}` : "No forecast yet"}
      </span>
    </div>
  );
}
