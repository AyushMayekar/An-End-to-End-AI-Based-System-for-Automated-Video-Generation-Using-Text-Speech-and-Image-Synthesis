"""
utils/logger.py
───────────────
Colored console logger for the entire application.
Import `log` from here everywhere — single unified logger.
"""

import logging
import sys

try:
    import colorlog
    _HAS_COLOR = True
except ImportError:
    _HAS_COLOR = False


def get_logger(name: str = "freedom_fighter_video") -> logging.Logger:
    """Return a configured logger. Call once per module."""
    logger = logging.getLogger(name)

    if logger.handlers:          # Prevent duplicate handlers on re-import
        return logger

    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)

    if _HAS_COLOR:
        fmt = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s [%(levelname)-8s]%(reset)s %(white)s%(message)s",
            datefmt="%H:%M:%S",
            log_colors={
                "DEBUG":    "cyan",
                "INFO":     "green",
                "WARNING":  "yellow",
                "ERROR":    "red",
                "CRITICAL": "bold_red",
            },
        )
    else:
        fmt = logging.Formatter(
            "%(asctime)s [%(levelname)-8s] %(message)s",
            datefmt="%H:%M:%S",
        )

    handler.setFormatter(fmt)
    logger.addHandler(handler)
    return logger


# Module-level default logger — import this directly
log = get_logger()
