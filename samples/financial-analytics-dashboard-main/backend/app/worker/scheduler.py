from __future__ import annotations

import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.core.database import SessionLocal, init_db
from app.worker.jobs import run_daily_pipeline

log = logging.getLogger(__name__)


def _daily_job() -> None:
    db = SessionLocal()
    try:
        report = run_daily_pipeline(db)
        log.info(
            "Daily pipeline finished: ingest %d/%d ok, train %d/%d ok",
            report.ingest.succeeded,
            len(report.ingest.results),
            report.train.succeeded,
            len(report.train.results),
        )
    except Exception:
        log.exception("Daily pipeline failed")
        db.rollback()
    finally:
        db.close()


def start_scheduler(*, run_on_start: bool | None = None) -> None:
    """Block forever, firing the daily pipeline on a US-market-friendly cron."""
    init_db()

    if run_on_start is None:
        run_on_start = settings.worker_run_on_start

    if run_on_start:
        log.info("Running daily pipeline immediately (worker_run_on_start)")
        _daily_job()

    sched = BlockingScheduler(timezone=settings.worker_timezone)
    sched.add_job(
        _daily_job,
        CronTrigger(
            hour=settings.worker_daily_hour,
            minute=settings.worker_daily_minute,
            day_of_week="mon-fri",
        ),
        id="daily_eod_and_train",
        replace_existing=True,
    )

    log.info(
        "Worker scheduler started (%s %02d:%02d mon-fri)",
        settings.worker_timezone,
        settings.worker_daily_hour,
        settings.worker_daily_minute,
    )
    sched.start()
