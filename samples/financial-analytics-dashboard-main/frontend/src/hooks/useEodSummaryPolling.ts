import { useEffect } from "react";
import {
  EOD_SUMMARY_POLL_MS,
  isRegularMarketOpen,
  msUntilMarketOpen,
  msUntilSessionClose,
} from "../utils/marketSession";

/**
 * Refresh EOD summary only when it can meaningfully change:
 * once at session close, then slowly while the market is closed.
 * No polling during regular hours — intraday handles live watchlist prices.
 */
export function useEodSummaryPolling(
  refreshSummary: () => Promise<void>,
  enabled: boolean,
) {
  useEffect(() => {
    if (!enabled) return;

    let cancelled = false;
    let pollId: number | undefined;
    let wakeId: number | undefined;

    const clearWake = () => {
      if (wakeId != null) window.clearTimeout(wakeId);
      wakeId = undefined;
    };

    const stopPolling = () => {
      if (pollId != null) window.clearInterval(pollId);
      pollId = undefined;
    };

    const startClosedMarketPolling = () => {
      stopPolling();
      pollId = window.setInterval(() => {
        if (!cancelled) void refreshSummary();
      }, EOD_SUMMARY_POLL_MS);
    };

    const scheduleMarketOpen = () => {
      clearWake();
      const openIn = msUntilMarketOpen();
      wakeId = window.setTimeout(() => {
        if (cancelled) return;
        stopPolling();
        scheduleSessionClose();
      }, Math.max(openIn, 1_000));
    };

    const scheduleSessionClose = () => {
      if (!isRegularMarketOpen()) {
        startClosedMarketPolling();
        scheduleMarketOpen();
        return;
      }

      clearWake();
      const closeIn = msUntilSessionClose();
      wakeId = window.setTimeout(async () => {
        if (cancelled) return;
        await refreshSummary();
        startClosedMarketPolling();
        scheduleMarketOpen();
      }, Math.max(closeIn, 1_000));
    };

    if (isRegularMarketOpen()) {
      scheduleSessionClose();
    } else {
      startClosedMarketPolling();
      scheduleMarketOpen();
    }

    return () => {
      cancelled = true;
      stopPolling();
      clearWake();
    };
  }, [enabled, refreshSummary]);
}
