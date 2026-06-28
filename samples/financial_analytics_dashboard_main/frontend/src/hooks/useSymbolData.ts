import { useEffect, useRef, useState } from "react";

import {

  fetchSymbolForecasts,

  fetchSymbolPrices,

  getErrorInfo,

  type ErrorInfo,

  type ForecastsResponse,

  type PricesResponse,

} from "../api/client";

import { isServerWakeupError } from "../api/errors";

import {

  getCachedForecasts,

  getStaleForecasts,

  setCachedForecasts,

  setCachedPrices,

} from "../api/symbolCache";

import { eodSessionDateKey } from "../utils/chart";
import { pickProphetForecast } from "../utils/forecasts";



function lastPriceSession(

  data: PricesResponse | null | undefined,

): string | null {

  const ts = data?.points?.at(-1)?.ts;

  return ts ? eodSessionDateKey(ts) : null;

}



export function useSymbolData(

  symbol: string,

  summaryLastSession?: string | null,

  hasAppData = false,

) {

  const [prices, setPrices] = useState<PricesResponse | null>(null);

  const [forecasts, setForecasts] = useState<ForecastsResponse | null>(null);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState<ErrorInfo | null>(null);

  const pricesRef = useRef<PricesResponse | null>(null);
  const forecastsRef = useRef<ForecastsResponse | null>(null);

  pricesRef.current = prices;
  forecastsRef.current = forecasts;



  useEffect(() => {

    let cancelled = false;



    const cachedForecasts =

      getCachedForecasts(symbol) ?? getStaleForecasts(symbol);



    setForecasts(cachedForecasts);

    setError(null);

    setLoading(true);

    setPrices(null);



    fetchSymbolPrices(symbol)

      .then((data) => {

        if (cancelled) return;

        setCachedPrices(symbol, data);

        setPrices(data);

      })

      .catch((e) => {

        if (cancelled) return;

        if (hasAppData || !isServerWakeupError(e)) {

          setError(getErrorInfo(e));

        }

      })

      .finally(() => {

        if (!cancelled) setLoading(false);

      });



    fetchSymbolForecasts(symbol)
      .then((data) => {
        if (cancelled) return;
        setCachedForecasts(symbol, data);
        setForecasts(data);
      })
      .catch((e) => {
        if (cancelled) return;
        if (hasAppData || !isServerWakeupError(e)) {
          setError((prev) => prev ?? getErrorInfo(e));
        }
        setForecasts((current) => current ?? getStaleForecasts(symbol));
      });



    return () => {

      cancelled = true;

    };

  }, [symbol, hasAppData]);



  const eodSessionRef = useRef<string | null>(null);

  useEffect(() => {
    if (!summaryLastSession) return;

    const previous = eodSessionRef.current;
    eodSessionRef.current = summaryLastSession;
    const sessionAdvanced =
      previous != null && summaryLastSession > previous;

    const currentSession = lastPriceSession(pricesRef.current);
    const pricesStale =
      !currentSession || currentSession < summaryLastSession;

    if (!sessionAdvanced && !pricesStale) return;

    let cancelled = false;

    if (pricesStale) {
      fetchSymbolPrices(symbol)
        .then((data) => {
          if (cancelled) return;
          setCachedPrices(symbol, data);
          setPrices(data);
        })
        .catch(() => {
          /* keep the series already on screen */
        });
    }

    const cachedForecast = pickProphetForecast(
      forecastsRef.current?.forecasts ?? getCachedForecasts(symbol)?.forecasts,
      summaryLastSession,
    );
    const forecastStale =
      !cachedForecast ||
      eodSessionDateKey(cachedForecast.forecast_for) <= summaryLastSession;

    if (sessionAdvanced || forecastStale) {
      fetchSymbolForecasts(symbol)
        .then((data) => {
          if (cancelled) return;
          setCachedForecasts(symbol, data);
          setForecasts(data);
        })
        .catch(() => {
          /* keep existing forecast on screen */
        });
    }

    return () => {
      cancelled = true;
    };
  }, [symbol, summaryLastSession]);



  return { prices, forecasts, loading, error };

}


