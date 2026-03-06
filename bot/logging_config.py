"""
Logging configuration for the Binance Futures Trading Bot.
Sets up both a rotating file handler and a coloured console handler.
"""

import logging
import logging.handlers
import os
from pathlib import Path


LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_FILE = LOG_DIR / "trading_bot.log"

# Formatter strings
FILE_FMT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
CONSOLE_FMT = "%(asctime)s | %(levelname)-8s | %(message)s"
DATE_FMT = "%Y-%m-%d %H:%M:%S"


def setup_logging(level: int = logging.DEBUG) -> None:
    """
    Configure root logger with:
      - RotatingFileHandler  → logs/trading_bot.log  (DEBUG+)
      - StreamHandler        → stderr               (WARNING+)
    Call once at application startup.
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    # Avoid adding duplicate handlers on repeated imports / tests
    if root.handlers:
        return

    root.setLevel(level)

    # ── File handler ──────────────────────────────────────────────────────────
    fh = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,   # 5 MB per file
        backupCount=5,
        encoding="utf-8",
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(FILE_FMT, datefmt=DATE_FMT))

    # ── Console handler (WARNING+ to keep CLI output clean) ───────────────────
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(logging.Formatter(CONSOLE_FMT, datefmt=DATE_FMT))

    root.addHandler(fh)
    root.addHandler(ch)


def get_logger(name: str) -> logging.Logger:
    """Return a named child logger (call *after* setup_logging)."""
    return logging.getLogger(name)
