from __future__ import annotations

import argparse
import logging
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingest daily OHLCV via Yahoo Finance.")
    parser.add_argument(
        "symbols",
        nargs="*",
        help="Ticker symbols (default: WORKER_SYMBOLS / built-in list)",
    )
    parser.add_argument(
        "--period",
        default=None,
        help="yfinance history period (default: WORKER_INGEST_PERIOD or 1y)",
    )
    parser.add_argument(
        "--no-info",
        action="store_true",
        help="Skip Yahoo info calls (faster; ticker names stay empty).",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    from app.core.config import settings
    from app.core.database import SessionLocal, init_db
    from app.worker.jobs import run_eod_ingest

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(message)s",
    )

    symbols = [s.upper() for s in args.symbols] if args.symbols else None
    period = args.period or settings.worker_ingest_period

    init_db()
    db = SessionLocal()
    try:
        report = run_eod_ingest(
            db,
            symbols=symbols,
            period=period,
            fetch_info=not args.no_info,
        )
        return 0 if report.failed == 0 else 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
