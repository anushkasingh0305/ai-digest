"""
Structured logging configuration for AI Digest system.
Provides JSON-formatted logs to both console and file.
"""

import logging
import logging.handlers
import json
import sys
import os
from datetime import datetime
from pathlib import Path


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        # Add extra fields from the log record
        if hasattr(record, "extra"):
            log_obj.update(record.extra)

        return json.dumps(log_obj)


def setup_logging(
    log_level: str = None,
    log_file: str = "logs/ai_digest.log",
    enable_console: bool = True,
) -> None:
    """
    Configure logging for the AI Digest system.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
                   Defaults to LOG_LEVEL env var or 'INFO'.
        log_file: Path to log file. Defaults to 'logs/ai_digest.log'.
        enable_console: Whether to log to console. Defaults to True.
    """
    # Determine log level from parameter or environment
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    log_level = getattr(logging, log_level, logging.INFO)

    # Create logs directory if it doesn't exist
    log_dir = Path(log_file).parent
    if log_file:
        log_dir.mkdir(parents=True, exist_ok=True)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # JSON formatter
    json_formatter = JSONFormatter()

    # File handler with rotation
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(json_formatter)
        root_logger.addHandler(file_handler)

    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(json_formatter)
        root_logger.addHandler(console_handler)

    # Set specific loggers
    logging.getLogger("aiosmtplib").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)
    logging.getLogger("praw").setLevel(logging.WARNING)
    logging.getLogger("feedparser").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.LoggerAdapter:
    """
    Get a logger instance with optional extra fields.

    Args:
        name: Logger name (typically __name__).

    Returns:
        LoggerAdapter for structured logging.
    """
    logger = logging.getLogger(name)
    return logging.LoggerAdapter(logger, {"extra": {}})
