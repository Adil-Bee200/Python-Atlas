import type { ForecastPoint } from "../api/client";
import { eodSessionDateKey } from "./chart";

const PROPHET_MODEL = "prophet_v1";

/** Pick the Prophet forecast for the next session after the latest ingested EOD bar. */
export function pickProphetForecast(
  forecasts: ForecastPoint[] | undefined,
  lastEodSession?: string | null,
): ForecastPoint | undefined {
  if (!forecasts?.length) return undefined;

  const prophet = forecasts.filter((f) => f.model_version === PROPHET_MODEL);
  const pool = prophet.length ? prophet : forecasts;

  if (lastEodSession) {
    const active = pool.find(
      (f) => eodSessionDateKey(f.forecast_for) > lastEodSession,
    );
    if (active) return active;
  }

  return pool.reduce<ForecastPoint | undefined>((best, f) => {
    if (!best) return f;
    const target = eodSessionDateKey(f.forecast_for);
    const bestTarget = eodSessionDateKey(best.forecast_for);
    if (target !== bestTarget) return target > bestTarget ? f : best;
    return new Date(f.created_at).getTime() > new Date(best.created_at).getTime()
      ? f
      : best;
  }, undefined);
}
