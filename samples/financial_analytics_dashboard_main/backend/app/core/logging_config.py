"""Configure root logging from ``settings.log_level``."""

from __future__ import annotations

import logging

from app.core.config import settings


def setup_logging() -> None:
    level = getattr(logging, settings.log_level, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
