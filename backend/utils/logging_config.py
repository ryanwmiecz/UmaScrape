"""
Logging configuration for the application.
Provides structured logging with file rotation and proper formatting.
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from config.settings import settings


def setup_logging(
    name: str = "umascrape",
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Configure application logging with console and file handlers.
    
    Args:
        name: Logger name
        log_file: Optional specific log file name (defaults to app.log)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Console handler with color formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    console_formatter = logging.Formatter(
        fmt='[%(asctime)s] %(levelname)-8s %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_file is None:
        log_file = "app.log"
    
    # Ensure log directory exists
    settings.LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    log_path = settings.LOG_DIR / log_file
    file_handler = RotatingFileHandler(
        filename=log_path,
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        fmt='[%(asctime)s] %(levelname)-8s [%(name)s:%(funcName)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the standard configuration.
    
    Args:
        name: Logger name (typically __name__ of the module)
    
    Returns:
        Configured logger instance
    """
    # If logger already exists with handlers, return it
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    
    # Otherwise, set it up
    return setup_logging(name)


# Don't setup default logger at module import time
# Let the application initialize it when needed
