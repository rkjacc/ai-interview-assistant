"""
Logging Module
Sets up two log files under gemini_interview/logs/:

  app.log       — Full application log: every step performed in the code,
                  including actions taken by the LLM (prompt details, response
                  metadata, Q&A parsing outcome).

  pii_audit.log — Resume-parsing audit log: proves that PII details and client
                  names detected in the candidate's resume are NOT forwarded to
                  the LLM.  Contains before/after snapshots and an explicit
                  AUDIT_PASS confirmation for each request.
"""

import logging
import logging.handlers
import sys
from pathlib import Path

# Both loggers write into gemini_interview/logs/
_LOGS_DIR = Path(__file__).parent.parent / "logs"
_LOGS_DIR.mkdir(exist_ok=True)

_APP_LOG_PATH      = _LOGS_DIR / "app.log"
_PII_AUDIT_LOG_PATH = _LOGS_DIR / "pii_audit.log"

# ---------------------------------------------------------------------------
# Formatter helpers
# ---------------------------------------------------------------------------
_APP_FMT = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(module)s:%(funcName)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

_AUDIT_FMT = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

_CONSOLE_FMT = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def get_app_logger() -> logging.Logger:
    """
    Return (and lazily configure) the full application logger.

    Writes to:
      • gemini_interview/logs/app.log  (DEBUG and above, daily rotation, 14-day
        backup) — captures every processing step and all LLM interactions.
      • stdout (INFO and above) — mirrors key events to the console so they are
        visible in the terminal where the server is running.
    """
    logger = logging.getLogger("gemini_interview.app")
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # -- rotating file handler -----------------------------------------------
    fh = logging.handlers.TimedRotatingFileHandler(
        _APP_LOG_PATH,
        when="midnight",
        backupCount=14,
        encoding="utf-8",
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(_APP_FMT)
    logger.addHandler(fh)

    # -- console handler (INFO+) ----------------------------------------------
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(_CONSOLE_FMT)
    logger.addHandler(ch)

    logger.propagate = False
    return logger


def get_pii_audit_logger() -> logging.Logger:
    """
    Return (and lazily configure) the PII audit logger.

    Writes ONLY to:
      • gemini_interview/logs/pii_audit.log  (INFO and above, daily rotation,
        30-day backup) — shows exactly what PII was detected, what was redacted,
        and what text was actually sent to the LLM, so any reader can verify that
        no raw PII or client names reached the model.
    """
    logger = logging.getLogger("gemini_interview.pii_audit")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    fh = logging.handlers.TimedRotatingFileHandler(
        _PII_AUDIT_LOG_PATH,
        when="midnight",
        backupCount=30,
        encoding="utf-8",
    )
    fh.setLevel(logging.INFO)
    fh.setFormatter(_AUDIT_FMT)
    logger.addHandler(fh)

    logger.propagate = False
    return logger
