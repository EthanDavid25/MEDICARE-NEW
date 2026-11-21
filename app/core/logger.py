"""MEDICARE application logging configuration."""
import logging
import logging.handlers
from pathlib import Path


def setup_logger(log_path: Path, log_level: str = "INFO") -> logging.Logger:
    """
    Configure the MEDICARE application logger.

    IMPORTANT: Patient PII must never be passed to log calls.
    Log file uses rotating handler (5 MB max, 3 backups).
    """
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("medicare")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    if logger.handlers:
        logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Rotating file handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_path, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.info("MEDICARE logger initialized. Log file: %s", log_path)
    return logger


def get_logger(name: str = "medicare") -> logging.Logger:
    return logging.getLogger(name)
